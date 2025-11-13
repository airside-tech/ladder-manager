'''
@file: room.py
@author: airside-tech

The room module defines the Room class, which represents a physical room and its attributes.
Also includes methods to manage data racks and tile occupancy within the room.

'''

class Room:
    '''
    Represents a physical data center room with dimensions, tile grid, and data racks.'''

    def __init__(self, room_id: str, num_tiles_x: int, num_tiles_y: int, 
                height: float, tile_size_xy = 0.6) -> None:
        self.room_id = room_id
        self.num_tiles_x = num_tiles_x
        self.num_tiles_y = num_tiles_y
        self.height = height  # in meters
        self.tile_size_xy = tile_size_xy  # default tile size in meters

        # Calculate dimensions
        self.length: float = num_tiles_x * tile_size_xy  # default tile size in meters
        self.width: float = num_tiles_y * tile_size_xy   # default tile size in meters

        # Establish a tile grid for the room. Each tile can be occupied or unoccupied.
        self.tile_grid: list[list[bool]] = [
            [False for _ in range(num_tiles_y)] for _ in range(num_tiles_x)
        ]  # False indicates unoccupied tile

        self.data_racks = []  # List of DataRack objects in the room
        self.obstacles = []   # List of Obstacle objects in the room



    @property
    def area(self) -> float:
        """Calculate the floor area of the room."""
        return self.length * self.width

    @property
    def volume(self) -> float:
        """Calculate the volume of the room."""
        return self.length * self.width * self.height
    

    def add_data_rack(self, rack) -> bool:
        """
        Add a data rack to the room and mark all occupied tiles.
        
        Args:
            rack: A DataRack object to place in the room
            
        Returns:
            bool: True if rack was successfully placed, False if tiles are out of bounds or already occupied
        """
        # Get all tiles this rack will occupy
        footprint = rack.get_tile_footprint()
        
        # Check if all tiles are within bounds and unoccupied
        for tile_x, tile_y in footprint:
            if tile_x < 0 or tile_x >= self.num_tiles_x or tile_y < 0 or tile_y >= self.num_tiles_y:
                return False  # Out of bounds
            if self.tile_grid[tile_x][tile_y]:
                return False  # Tile already occupied
        
        # All tiles are valid, mark them as occupied
        for tile_x, tile_y in footprint:
            self.tile_grid[tile_x][tile_y] = True
        
        # Store the rack reference
        self.data_racks.append(rack)
        return True

    def remove_data_rack(self, rack) -> bool:
        """
        Remove a data rack from the room and free its tiles.
        
        Args:
            rack: The DataRack object to remove
        Returns:
            bool: True if rack was removed, False if not found
        """
        if rack not in self.data_racks:
            return False
        
        # Free all tiles occupied by this rack
        footprint = rack.get_tile_footprint()
        for tile_x, tile_y in footprint:
            if 0 <= tile_x < self.num_tiles_x and 0 <= tile_y < self.num_tiles_y:
                self.tile_grid[tile_x][tile_y] = False
        
        # Remove the rack reference
        self.data_racks.remove(rack)
        return True


    def is_tile_occupied(self, tile_x: int, tile_y: int) -> bool:
        """Check if a specific tile is occupied."""
        return self.tile_grid[tile_x][tile_y]  


    def get_occupied_tiles(self) -> list[tuple[int, int]]:
        """Get a list of all occupied tiles in the room."""
        occupied_tiles = []
        for x in range(self.num_tiles_x):
            for y in range(self.num_tiles_y):
                if self.tile_grid[x][y]:
                    occupied_tiles.append((x, y))
        return occupied_tiles   


    def get_unoccupied_tiles(self) -> list[tuple[int, int]]:
        """Get a list of all unoccupied tiles in the room."""
        unoccupied_tiles = []
        for x in range(self.num_tiles_x):
            for y in range(self.num_tiles_y):
                if not self.tile_grid[x][y]:
                    unoccupied_tiles.append((x, y))
        return unoccupied_tiles
    
    def add_obstacle(self, obstacle) -> bool:
        """
        Add an obstacle to the room and mark all occupied tiles.
        
        Args:
            obstacle: An Obstacle object to place in the room
            
        Returns:
            bool: True if obstacle was successfully placed, False if tiles are out of bounds or already occupied
        """
        # Get all tiles this obstacle will occupy
        footprint = obstacle.get_tile_footprint()
        
        # Check if all tiles are within bounds and unoccupied
        for tile_x, tile_y in footprint:
            if tile_x < 0 or tile_x >= self.num_tiles_x or tile_y < 0 or tile_y >= self.num_tiles_y:
                return False  # Out of bounds
            if self.tile_grid[tile_x][tile_y]:
                return False  # Tile already occupied
        
        # All tiles are valid, mark them as occupied
        for tile_x, tile_y in footprint:
            self.tile_grid[tile_x][tile_y] = True
        
        # Store the obstacle reference
        self.obstacles.append(obstacle)
        return True
    
    def remove_obstacle(self, obstacle) -> bool:
        """
        Remove an obstacle from the room and free its tiles.
        
        Args:
            obstacle: The Obstacle object to remove
            
        Returns:
            bool: True if obstacle was removed, False if not found
        """
        if obstacle not in self.obstacles:
            return False
        
        # Free all tiles occupied by this obstacle
        footprint = obstacle.get_tile_footprint()
        for tile_x, tile_y in footprint:
            if 0 <= tile_x < self.num_tiles_x and 0 <= tile_y < self.num_tiles_y:
                self.tile_grid[tile_x][tile_y] = False
        
        # Remove the obstacle reference
        self.obstacles.remove(obstacle)
        return True