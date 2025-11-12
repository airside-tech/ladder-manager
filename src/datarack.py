class DataRack:
    '''
    Represents a data rack within a room.
    '''
    def __init__(self, rack_id: str, position_x: int, position_y: int, rack_units: int, 
                 width_tiles: int = 1, depth_tiles: int = 1) -> None:
        self.rack_id = rack_id
        self.position_x = position_x  # Tile x starting coordinate
        self.position_y = position_y  # Tile y starting coordinate
        self.rack_units = rack_units
        self.width_tiles = width_tiles  # Number of tiles occupied in x direction
        self.depth_tiles = depth_tiles  # Number of tiles occupied in y direction

        self.rack_height_meters = rack_units * 0.04445  # Convert rack units to meters (1U = 44.45mm)
        self.rack_height_inches = rack_units * 1.75  # Convert rack units to inches (1U = 1.75 inches)
        self.rack_weight_kg_estimated = rack_units * 4.5  # Convert rack units to weight (1U = 4.5kg)

    def get_rack_id(self) -> str:
        """Return the rack ID."""
        return self.rack_id
    
    def get_rack_position(self) -> tuple[int, int]:
        """Return the (x, y) position of the data rack."""
        return (self.position_x, self.position_y)   

    def get_rack_height_meters(self) -> float:
        """Return the height of the data rack in meters."""
        return self.rack_height_meters

    def get_rack_weight_estimated(self) -> float:
        """Return the weight of the data rack in kilograms."""
        return self.rack_weight_kg_estimated

    def get_rack_units(self) -> int:
        """Return the number of rack units."""
        return self.rack_units


    def set_rack_units(self, new_units: int) -> None:
        """Update the number of rack units."""
        self.rack_units = new_units
        self.rack_height_meters = new_units * 0.04445  # Update height in meters
        self.rack_height_inches = new_units * 1.75  # Update height in inches
        self.rack_weight_kg_estimated = new_units * 4.5  # Update weight in kg


    def set_rack_position(self, new_x: int, new_y: int) -> None:

        """Update the position of the data rack."""
        self.position_x = new_x
        self.position_y = new_y


    
    def get_tile_footprint(self) -> list[tuple[int, int]]:
        """Get a list of all tile coordinates occupied by this rack."""
        tiles = []
        for dx in range(self.width_tiles):
            for dy in range(self.depth_tiles):
                tiles.append((self.position_x + dx, self.position_y + dy))
        return tiles

    def get_rack_info(self) -> dict:
        """Get a dictionary of rack information."""
        return {
            "rack_id": self.rack_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "rack_units": self.rack_units,
            "width_tiles": self.width_tiles,
            "depth_tiles": self.depth_tiles,
            "rack_height_meters": self.rack_height_meters,
            "rack_height_inches": self.rack_height_inches,
            "rack_weight_kg_estimated": self.rack_weight_kg_estimated,
        } 
    

    def __repr__(self) -> str:
        return f"DataRack(rack_id={self.rack_id}, position=({self.position_x}, {self.position_y}), rack_units={self.rack_units}, footprint={self.width_tiles}x{self.depth_tiles})"
    
  