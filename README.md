# Cable Ladder Manager

The manager is a tool to plan and route cable ladders inside data centers and equipment rooms.
All equipment rooms are defined as a room with a datafloor given by the matrix of 60 x 60 cm tiles.
The back-end is written in Python. Front-end framework is not decided.

## Features

### Core Classes

#### Room
- **Physical room representation** with configurable tile grid dimensions
- **Tile-based floor layout** with customizable tile size (default: 0.6m × 0.6m)
- **Multi-tile data rack placement** with collision detection and bounds checking
- **Obstacle support** - place physical barriers (ducts, beams, support columns) that block tile occupancy
- **Area and volume calculations** for space planning
- **Tile occupancy tracking** - query occupied and unoccupied tiles
- Prevents overlapping rack and obstacle placement automatically

#### DataRack
- **Data center rack management** with standard rack unit (U) calculations
- **Multi-tile footprint support** - racks can occupy 1×1, 2×2, 3×2, or custom tile areas
- **Automatic dimension calculations**:
  - Height in meters (1U = 44.45mm) and inches (1U = 1.75")
  - Estimated weight (1U = 4.5kg)
- **Positioning system** with tile-based coordinates
- **Tile footprint calculation** - get all tiles occupied by a rack
- Rack information export to dictionary format

#### Obstacle
- **Physical barrier representation** for non-movable structures
- **Tile-based footprint** - obstacles occupy specific tiles and prevent ladder/rack placement
- **Configurable dimensions** - width, depth (in tiles), and height (in meters)
- **Examples:** Ventilation ducts, support beams, columns, HVAC equipment

#### Ladder (Section-based)
- **Modular ladder construction** from individual sections
- **Section properties**:
  - Position coordinates (x, y)
  - Length and orientation (horizontal/vertical)
  - Bend degree for curved sections (positive = right, negative = left)
  - Width and material customization (30cm, 60cm, 90cm, 120cm widths)
- **Visual capacity indication** - wider ladders support more cable runs
- **Total length calculation** across all sections
- **Support for mixed orientations** and materials in a single ladder

### Testing

Comprehensive test suite with 60+ tests covering:
- **Unit tests** for DataRack, Ladder, Section, and Room classes
- **Integration tests** for rack placement and tile occupancy
- **Edge case validation** (bounds checking, overlaps, zero values)

Run tests with:
```bash
pytest src/tests/ -v
```

### Example Usage

#### Multi-Tile Rack Placement
```python
from room import Room
from datarack import DataRack

# Create a 10×10 tile room (6m × 6m physical)
room = Room(room_id="DC-01", num_tiles_x=10, num_tiles_y=10, height=3.0)

# Place a 2×2 tile rack (42U)
rack = DataRack("RACK-01", position_x=2, position_y=3, rack_units=42,
                width_tiles=2, depth_tiles=2)

if room.add_data_rack(rack):
    print(f"Rack placed at {rack.get_rack_position()}")
    print(f"Occupying tiles: {rack.get_tile_footprint()}")
    print(f"Height: {rack.get_rack_height_meters():.2f}m")
else:
    print("Placement failed - tiles occupied or out of bounds")
```

#### Ladder Construction
```python
from ladder import Ladder, Section

# Create a ladder with multiple sections
ladder = Ladder(ladder_id="LAD-001")

# Add horizontal section
ladder.add_section(Section("SEC-01", x_coord=0.0, y_coord=0.0,
                          length=1.5, orientation="horizontal"))

# Add vertical section
ladder.add_section(Section("SEC-02", x_coord=1.5, y_coord=0.0,
                          length=2.0, orientation="vertical"))

# Add curved section (15° bend)
ladder.add_section(Section("SEC-03", x_coord=1.5, y_coord=2.0,
                          length=1.5, orientation="horizontal",
                          bend_degree=15.0))

print(f"Total ladder length: {ladder.total_length}m")
```

#### Running the Example
```bash
python example_multi_tile_racks.py
```

### GUI (pygame)

A fully interactive GUI for designing data center layouts with racks, obstacles, and cable ladders.

**Room size:** 25×20 tiles (expandable via zoom)

Run the GUI:
```bash
python gui_ladder_manager.py
```

#### Controls:

**Placement:**
- R: Place a 2×2 rack
- B: Place a 1×1 obstacle
- T: Toggle between rack/obstacle placement modes

**Ladder Mode:**
- L: Toggle ladder mode on/off
- Click: Set start point, then end point to place ladder segment
- N: Start a new ladder (finalize current one)
- U: Undo the last section
- X: Delete the last ladder

**Selection & Editing:**
- Click: Select a ladder section (shows width and highlights in yellow)
- DELETE: Remove the selected section
- C: Clear selection

**View:**
- Mouse Wheel: Zoom in/out (0.3x to 3.0x)
- H: Toggle help overlay

**File Operations:**
- S: Save layout to `layout.json`
- O: Load layout from `layout.json`
- ESC: Exit

#### Features:

**Visual Indicators:**
- Occupied tiles have a subtle dark overlay
- Racks are shown in blue with labels
- Obstacles display with brown hazard stripes
- Ladder preview snaps to horizontal/vertical alignment
- Hover previews: green (placeable), red (blocked), brown (obstacle)

**Ladder Width Visualization:**
- Ladders render with width proportional to their capacity
- Color-coded for easy identification:
  - 🟠 Orange: 30cm (small capacity)
  - 🟡 Yellow-Orange: 60cm (medium capacity)
  - 🟢 Yellow-Green: 90cm (good capacity)
  - 💚 Green: 120cm+ (high capacity)
- Selected sections display their width in cm

**Zoom & Navigation:**
- Use mouse wheel to zoom from 0.3x (overview) to 3.0x (detail)
- Larger 25×20 tile room provides more planning space

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
ladder-manager/
├── src/
│   ├── datarack.py      # DataRack class for rack management
│   ├── obstacle.py      # Obstacle class for physical barriers
│   ├── ladder.py        # Ladder and Section classes
│   ├── room.py          # Room class with tile grid
│   └── tests/
│       ├── test_datarack.py
│       ├── test_ladder.py
│       ├── test_room.py
│       └── test_section.py
├── gui_ladder_manager.py  # Interactive pygame GUI
├── example_multi_tile_racks.py
├── requirements.txt
└── README.md
```

## Roadmap (TODO)

- [ ] Consider running the application in docker containers
- [ ] Decouple back-end, database handling, and front-end
- [ ] Database handler - store and retrieve data
- [ ] Cable routing algorithms between racks
- [ ] Ladder path optimization
- [ ] 3D visualization of room layout
- [ ] Export layouts to CAD formats

---

**airside-tech**, November 12, 2025
