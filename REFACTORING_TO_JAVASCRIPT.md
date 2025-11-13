# Refactoring Guide: Python/Pygame → JavaScript Frontend

## Overview
This guide outlines the architectural changes needed to migrate from the current pygame-based GUI to a modern JavaScript frontend while keeping Python as the backend.

---

## 1. Architecture Change: Separation of Concerns

### Current Architecture (Monolithic)
```
┌─────────────────────────────────────┐
│   gui_ladder_manager.py (pygame)    │
│  ┌───────────────────────────────┐  │
│  │  Rendering (draw_*)           │  │
│  │  Event Handling (keyboard)    │  │
│  │  State Management             │  │
│  │  Business Logic               │  │
│  └───────────────────────────────┘  │
│              ↓                      │
│  ┌───────────────────────────────┐  │
│  │  Domain Models (Room, Rack,   │  │
│  │  Ladder, Obstacle)            │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### New Architecture (Client-Server)
```
┌──────────────────────────┐         ┌─────────────────────────┐
│   JavaScript Frontend    │         │   Python Backend        │
│   (React/Vue/Svelte)     │◄───────►│   (FastAPI/Flask)       │
│                          │  REST   │                         │
│  ┌────────────────────┐  │   or    │  ┌──────────────────┐  │
│  │ UI Components      │  │ WebSock │  │ API Endpoints    │  │
│  │ - Canvas Rendering │  │         │  │ - POST /racks    │  │
│  │ - Event Handlers   │  │         │  │ - GET /layout    │  │
│  │ - State (Redux)    │  │         │  │ - PUT /ladders   │  │
│  └────────────────────┘  │         │  └──────────────────┘  │
│                          │         │           ↓            │
│                          │         │  ┌──────────────────┐  │
│                          │         │  │ Domain Models    │  │
│                          │         │  │ (Room, Rack,     │  │
│                          │         │  │  Ladder, etc.)   │  │
│                          │         │  └──────────────────┘  │
└──────────────────────────┘         └─────────────────────────┘
```

---

## 2. Technology Stack Recommendations

### Backend (Python)
- **Framework**: FastAPI (modern, async, automatic OpenAPI docs)
- **Alternative**: Flask with Flask-RESTX
- **Database**: SQLite (simple) or PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Serialization**: Pydantic models (FastAPI native)

### Frontend (JavaScript)
**Option A: React + Konva.js (Recommended)**
- React for component architecture
- Konva.js for canvas rendering (similar to pygame)
- React-Konva for React integration
- Redux Toolkit for state management
- Axios for API calls

**Option B: Vue.js + Fabric.js**
- Vue 3 with Composition API
- Fabric.js for canvas manipulation
- Pinia for state management

**Option C: Svelte + Pixi.js**
- Svelte (simpler, less boilerplate)
- Pixi.js (high-performance 2D rendering)
- Built-in state management

### Why Konva.js/React is Best for This Project:
1. **Similar to Pygame**: Canvas-based rendering with shapes, lines, rectangles
2. **React Ecosystem**: Huge community, lots of UI libraries
3. **TypeScript Support**: Type safety for complex state
4. **Easy Event Handling**: Click, drag, zoom built-in
5. **Performance**: Hardware-accelerated canvas

---

## 3. Backend API Design (FastAPI)

### File Structure
```
ladder-manager/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── rooms.py        # Room endpoints
│   │   │   ├── racks.py        # Rack endpoints
│   │   │   ├── ladders.py      # Ladder endpoints
│   │   │   ├── obstacles.py    # Obstacle endpoints
│   │   │   └── layouts.py      # Save/load layouts
│   │   └── schemas.py          # Pydantic models
│   ├── models/                 # Domain models (from src/)
│   │   ├── room.py
│   │   ├── datarack.py
│   │   ├── ladder.py
│   │   └── obstacle.py
│   ├── database.py             # DB connection
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── store/
└── README.md
```

### Key API Endpoints

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import rooms, racks, ladders, obstacles, layouts

app = FastAPI(title="Cable Ladder Manager API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(racks.router, prefix="/api/racks", tags=["racks"])
app.include_router(ladders.router, prefix="/api/ladders", tags=["ladders"])
app.include_router(obstacles.router, prefix="/api/obstacles", tags=["obstacles"])
app.include_router(layouts.router, prefix="/api/layouts", tags=["layouts"])
```

### Example Endpoint (Racks)

```python
# backend/api/routes/racks.py
from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas import RackCreate, RackResponse, RackUpdate
from models.room import Room
from models.datarack import DataRack

router = APIRouter()

# In-memory storage (replace with database)
rooms = {}

@router.post("/", response_model=RackResponse)
def create_rack(rack: RackCreate, room_id: str):
    """Add a new rack to a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    new_rack = DataRack(
        rack_id=rack.rack_id,
        position_x=rack.position_x,
        position_y=rack.position_y,
        rack_units=rack.rack_units,
        width_tiles=rack.width_tiles,
        depth_tiles=rack.depth_tiles
    )
    
    if not room.add_data_rack(new_rack):
        raise HTTPException(status_code=400, detail="Cannot place rack - tiles occupied")
    
    return RackResponse.from_orm(new_rack)

@router.get("/{room_id}", response_model=List[RackResponse])
def get_racks(room_id: str):
    """Get all racks in a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return [RackResponse.from_orm(r) for r in rooms[room_id].data_racks]

@router.delete("/{rack_id}")
def delete_rack(rack_id: str, room_id: str):
    """Delete a rack"""
    # Implementation here
    pass
```

### Pydantic Schemas

```python
# backend/api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class RackBase(BaseModel):
    rack_id: str
    position_x: int
    position_y: int
    rack_units: int
    width_tiles: int = 2
    depth_tiles: int = 2

class RackCreate(RackBase):
    pass

class RackUpdate(BaseModel):
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    rack_units: Optional[int] = None

class RackResponse(RackBase):
    rack_height_meters: float
    rack_weight_kg_estimated: float
    
    class Config:
        orm_mode = True

class SectionBase(BaseModel):
    section_id: str
    x_coord: float
    y_coord: float
    length: float
    orientation: str
    bend_degree: float = 0.0
    width: float = 30.0
    material: str = "aluminum"

class LadderCreate(BaseModel):
    ladder_id: str
    sections: List[SectionBase]

class ObstacleCreate(BaseModel):
    obstacle_id: str
    position_x: int
    position_y: int
    width_tiles: int = 1
    depth_tiles: int = 1
    height: float = 1.0

class LayoutResponse(BaseModel):
    room_id: str
    num_tiles_x: int
    num_tiles_y: int
    height: float
    racks: List[RackResponse]
    obstacles: List[ObstacleCreate]
    ladders: List[LadderCreate]
```

---

## 4. Frontend Implementation (React + Konva)

### File Structure
```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── Canvas/
│   │   │   ├── Grid.jsx              # Tile grid rendering
│   │   │   ├── Rack.jsx              # Single rack component
│   │   │   ├── Obstacle.jsx          # Single obstacle
│   │   │   ├── LadderSection.jsx     # Ladder section
│   │   │   └── Canvas.jsx            # Main canvas container
│   │   ├── Toolbar/
│   │   │   ├── PlacementTools.jsx    # Rack/Obstacle buttons
│   │   │   ├── LadderTools.jsx       # Ladder mode controls
│   │   │   ├── ZoomControls.jsx      # Zoom in/out
│   │   │   └── Toolbar.jsx           # Main toolbar
│   │   ├── Modals/
│   │   │   ├── HelpModal.jsx         # Help/controls overlay
│   │   │   ├── SaveLoadModal.jsx     # Save/load layouts
│   │   │   └── PropertiesPanel.jsx   # Edit rack/section properties
│   │   └── App.jsx
│   ├── services/
│   │   └── api.js                    # API client (axios)
│   ├── store/
│   │   ├── roomSlice.js              # Room state
│   │   ├── racksSlice.js             # Racks state
│   │   ├── laddersSlice.js           # Ladders state
│   │   ├── uiSlice.js                # UI state (zoom, modes)
│   │   └── store.js                  # Redux store config
│   ├── utils/
│   │   ├── coordinates.js            # Tile<->pixel conversion
│   │   └── colors.js                 # Color definitions
│   └── index.js
├── package.json
└── README.md
```

### Main Canvas Component (React-Konva)

```jsx
// src/components/Canvas/Canvas.jsx
import React, { useRef, useEffect } from 'react';
import { Stage, Layer } from 'react-konva';
import { useSelector, useDispatch } from 'react-redux';
import Grid from './Grid';
import Rack from './Rack';
import Obstacle from './Obstacle';
import LadderSection from './LadderSection';

const Canvas = () => {
  const dispatch = useDispatch();
  const stageRef = useRef(null);
  
  // Get state from Redux
  const { room, racks, obstacles, ladders } = useSelector(state => state.layout);
  const { zoom, offset } = useSelector(state => state.ui);
  
  const handleWheel = (e) => {
    e.evt.preventDefault();
    
    const stage = stageRef.current;
    const oldScale = stage.scaleX();
    const pointer = stage.getPointerPosition();
    
    const scaleBy = 1.1;
    const newScale = e.evt.deltaY > 0 
      ? oldScale / scaleBy 
      : oldScale * scaleBy;
    
    // Clamp zoom
    const clampedScale = Math.max(0.3, Math.min(3.0, newScale));
    
    // Calculate new position to zoom towards mouse
    const mousePointTo = {
      x: (pointer.x - stage.x()) / oldScale,
      y: (pointer.y - stage.y()) / oldScale,
    };
    
    dispatch(setZoom({
      zoom: clampedScale,
      offset: {
        x: pointer.x - mousePointTo.x * clampedScale,
        y: pointer.y - mousePointTo.y * clampedScale,
      }
    }));
  };
  
  const handleClick = (e) => {
    // Handle click events for placement
    const stage = e.target.getStage();
    const pos = stage.getPointerPosition();
    
    // Convert pixel to tile coordinates
    const tileX = Math.floor((pos.x - offset.x) / (TILE_SIZE * zoom));
    const tileY = Math.floor((pos.y - offset.y) / (TILE_SIZE * zoom));
    
    // Dispatch appropriate action based on mode
    // dispatch(placeRack({ x: tileX, y: tileY }));
  };
  
  return (
    <Stage
      ref={stageRef}
      width={window.innerWidth}
      height={window.innerHeight}
      scaleX={zoom}
      scaleY={zoom}
      x={offset.x}
      y={offset.y}
      onWheel={handleWheel}
      onClick={handleClick}
    >
      <Layer>
        <Grid 
          numTilesX={room.num_tiles_x} 
          numTilesY={room.num_tiles_y} 
        />
        
        {racks.map(rack => (
          <Rack key={rack.rack_id} rack={rack} />
        ))}
        
        {obstacles.map(obs => (
          <Obstacle key={obs.obstacle_id} obstacle={obs} />
        ))}
        
        {ladders.map(ladder => 
          ladder.sections.map(section => (
            <LadderSection 
              key={section.section_id} 
              section={section} 
            />
          ))
        )}
      </Layer>
    </Stage>
  );
};

export default Canvas;
```

### Rack Component

```jsx
// src/components/Canvas/Rack.jsx
import React from 'react';
import { Group, Rect, Text } from 'react-konva';
import { TILE_SIZE, COLORS } from '../../utils/constants';

const Rack = ({ rack }) => {
  const x = rack.position_x * TILE_SIZE;
  const y = rack.position_y * TILE_SIZE;
  const width = rack.width_tiles * TILE_SIZE;
  const height = rack.depth_tiles * TILE_SIZE;
  
  return (
    <Group>
      {/* Main rack body */}
      <Rect
        x={x + 2}
        y={y + 2}
        width={width - 4}
        height={height - 4}
        fill={COLORS.DARK_BLUE}
        stroke={COLORS.BLUE}
        strokeWidth={2}
      />
      
      {/* Rack label */}
      <Text
        x={x}
        y={y + height / 2 - 10}
        width={width}
        text={rack.rack_id}
        fontSize={14}
        fill="white"
        align="center"
      />
    </Group>
  );
};

export default Rack;
```

### API Service

```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const roomAPI = {
  getRoom: (roomId) => api.get(`/rooms/${roomId}`),
  createRoom: (roomData) => api.post('/rooms', roomData),
  updateRoom: (roomId, roomData) => api.put(`/rooms/${roomId}`, roomData),
};

export const rackAPI = {
  getRacks: (roomId) => api.get(`/racks/${roomId}`),
  createRack: (roomId, rackData) => api.post(`/racks?room_id=${roomId}`, rackData),
  updateRack: (rackId, rackData) => api.put(`/racks/${rackId}`, rackData),
  deleteRack: (rackId, roomId) => api.delete(`/racks/${rackId}?room_id=${roomId}`),
};

export const ladderAPI = {
  getLadders: (roomId) => api.get(`/ladders/${roomId}`),
  createLadder: (roomId, ladderData) => api.post(`/ladders?room_id=${roomId}`, ladderData),
  updateLadder: (ladderId, ladderData) => api.put(`/ladders/${ladderId}`, ladderData),
  deleteLadder: (ladderId) => api.delete(`/ladders/${ladderId}`),
  deleteSection: (ladderId, sectionId) => api.delete(`/ladders/${ladderId}/sections/${sectionId}`),
};

export const obstacleAPI = {
  getObstacles: (roomId) => api.get(`/obstacles/${roomId}`),
  createObstacle: (roomId, obstacleData) => api.post(`/obstacles?room_id=${roomId}`, obstacleData),
  deleteObstacle: (obstacleId, roomId) => api.delete(`/obstacles/${obstacleId}?room_id=${roomId}`),
};

export const layoutAPI = {
  saveLayout: (layoutData) => api.post('/layouts', layoutData),
  loadLayout: (layoutId) => api.get(`/layouts/${layoutId}`),
  listLayouts: () => api.get('/layouts'),
};

export default api;
```

### Redux Store Example

```javascript
// src/store/racksSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { rackAPI } from '../services/api';

export const fetchRacks = createAsyncThunk(
  'racks/fetchRacks',
  async (roomId) => {
    const response = await rackAPI.getRacks(roomId);
    return response.data;
  }
);

export const addRack = createAsyncThunk(
  'racks/addRack',
  async ({ roomId, rackData }) => {
    const response = await rackAPI.createRack(roomId, rackData);
    return response.data;
  }
);

const racksSlice = createSlice({
  name: 'racks',
  initialState: {
    items: [],
    loading: false,
    error: null,
  },
  reducers: {
    selectRack: (state, action) => {
      state.selectedRackId = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRacks.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchRacks.fulfilled, (state, action) => {
        state.items = action.payload;
        state.loading = false;
      })
      .addCase(addRack.fulfilled, (state, action) => {
        state.items.push(action.payload);
      });
  },
});

export const { selectRack } = racksSlice.actions;
export default racksSlice.reducer;
```

---

## 5. Key Migration Steps

### Step 1: Create Backend API (Week 1)
1. Set up FastAPI project structure
2. Convert existing domain models to work with FastAPI
3. Create Pydantic schemas for all models
4. Implement CRUD endpoints for Room, Rack, Ladder, Obstacle
5. Add save/load layout endpoints
6. Write API tests
7. Document API with Swagger/OpenAPI

### Step 2: Set Up Frontend Scaffold (Week 1-2)
1. Initialize React app with Create React App or Vite
2. Install dependencies: react-konva, redux-toolkit, axios
3. Set up project structure
4. Configure Redux store
5. Create API service layer
6. Build basic Canvas component

### Step 3: Implement Core Features (Week 2-3)
1. **Grid Rendering**: Render tile grid with Konva
2. **Rack Placement**: Click to place, drag to move
3. **Obstacle Placement**: Similar to racks
4. **Ladder Drawing**: Click-and-drag for sections
5. **Selection**: Click to select items, show properties
6. **Zoom/Pan**: Mouse wheel zoom, drag to pan

### Step 4: Add Advanced Features (Week 3-4)
1. **Undo/Redo**: Command pattern in Redux
2. **Keyboard Shortcuts**: Hotkeys for modes
3. **Save/Load**: Dialog with layout management
4. **Properties Panel**: Edit rack units, ladder width, etc.
5. **Validation**: Real-time collision detection
6. **Export**: PDF/PNG export

### Step 5: Polish & Deploy (Week 4-5)
1. **Styling**: Modern UI with Material-UI or Tailwind
2. **Responsive**: Mobile-friendly layout
3. **Testing**: Unit tests, E2E tests with Cypress
4. **Performance**: Optimize rendering for large rooms
5. **Deploy**: Docker containers, cloud hosting

---

## 6. Key Differences & Improvements

### What Changes
| Pygame | React + Konva |
|--------|---------------|
| Immediate mode rendering | Retained mode (objects persist) |
| Manual event loop | React handles rendering loop |
| All state in one class | Redux with separate slices |
| Python types | TypeScript for type safety |
| Local file save/load | Database + API |
| Desktop only | Web-based, works anywhere |

### What Gets Better
1. **Collaboration**: Multiple users can work on same layout (WebSocket)
2. **Undo/Redo**: Built into Redux time-travel
3. **Drag and Drop**: Konva has built-in drag support
4. **Animations**: Smooth transitions for adding/removing items
5. **Responsive**: Works on tablets and large monitors
6. **Persistence**: Auto-save to database
7. **Sharing**: Share layouts via URL
8. **Export**: Export to various formats (PDF, PNG, DXF)

---

## 7. Package.json Example

```json
{
  "name": "ladder-manager-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-konva": "^18.2.10",
    "konva": "^9.2.0",
    "@reduxjs/toolkit": "^1.9.7",
    "react-redux": "^8.1.3",
    "axios": "^1.6.0",
    "@mui/material": "^5.14.18",
    "@mui/icons-material": "^5.14.18",
    "react-router-dom": "^6.18.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.2",
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "eslint": "^8.54.0",
    "vitest": "^1.0.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest"
  }
}
```

---

## 8. Requirements.txt for Backend

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

---

## 9. Quick Start Commands

### Backend
```bash
cd ladder-manager/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd ladder-manager/frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

---

## 10. Migration Effort Estimate

**Total Time**: 4-6 weeks (1 developer)

- Backend API: 1-2 weeks
- Frontend Core: 2-3 weeks  
- Features & Polish: 1-2 weeks
- Testing & Deployment: 1 week

**Skills Required**:
- Python (FastAPI)
- JavaScript/React
- Canvas/Konva
- Redux state management
- REST API design
- Database design (optional)

---

## 11. Bonus: WebSocket for Real-Time Collaboration

```python
# backend/main.py - Add WebSocket support
from fastapi import WebSocket, WebSocketManager

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast changes to all connected clients
            await manager.broadcast({
                "room_id": room_id,
                "action": data["action"],
                "data": data["data"]
            })
    except WebSocketDisconnect:
        manager.active_connections.remove(websocket)
```

```javascript
// Frontend WebSocket client
import { useEffect } from 'react';
import { useDispatch } from 'react-redux';

const useRealtimeSync = (roomId) => {
  const dispatch = useDispatch();
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${roomId}`);
    
    ws.onmessage = (event) => {
      const { action, data } = JSON.parse(event.data);
      
      switch(action) {
        case 'rack_added':
          dispatch(addRackFromServer(data));
          break;
        case 'ladder_updated':
          dispatch(updateLadderFromServer(data));
          break;
        // ... handle other actions
      }
    };
    
    return () => ws.close();
  }, [roomId, dispatch]);
};
```

---

## Summary

The migration from pygame to JavaScript frontend provides:
- **Better UX**: Modern web UI, responsive, shareable
- **Scalability**: API-based, multi-user support
- **Maintainability**: Separation of concerns, testable
- **Flexibility**: Easy to add features, integrate with other tools
- **Deployment**: Web-based, no installation needed

The Python domain models (Room, Rack, Ladder, Obstacle) stay largely the same, just exposed via REST API instead of direct pygame rendering.
