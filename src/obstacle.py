'''
@file: src/obstacle.py
@author: airside-tech

Obstacle objects represent physical barriers within a layout. This can include ventilation ducts,
support beams, or any other non-movable structures that may impact ladder placement or routing.

'''

class Obstacle:
    def __init__(self, obstacle_id: str, position_x: int, position_y: int,
                 width_tiles: int = 1, depth_tiles: int = 1, height: float = 1.0) -> None:
        self.obstacle_id = obstacle_id
        self.position_x = position_x  # Tile x starting coordinate
        self.position_y = position_y  # Tile y starting coordinate
        self.width_tiles = width_tiles  # Number of tiles occupied in x direction
        self.depth_tiles = depth_tiles  # Number of tiles occupied in y direction
        self.height = height            # height in meters

    def get_obstacle_id(self) -> str:
        """Return the obstacle ID."""
        return self.obstacle_id

    def get_position(self) -> tuple[int, int]:
        """Return the (x, y) position of the obstacle."""
        return (self.position_x, self.position_y)

    def get_dimensions(self) -> tuple[int, int, float]:
        """ Return the dimensions (width_tiles, depth_tiles, height) of the obstacle."""
        return (self.width_tiles, self.depth_tiles, self.height)
    
    def get_tile_footprint(self) -> list[tuple[int, int]]:
        """Get a list of all tile coordinates occupied by this obstacle."""
        tiles = []
        for dx in range(self.width_tiles):
            for dy in range(self.depth_tiles):
                tiles.append((self.position_x + dx, self.position_y + dy))
        return tiles
    
    def __repr__(self) -> str:
        return f"Obstacle(id={self.obstacle_id}, position=({self.position_x}, {self.position_y}), footprint={self.width_tiles}x{self.depth_tiles})"
