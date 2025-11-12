#!/usr/bin/env python3
'''
Example script demonstrating multi-tile DataRack placement in a Room (headless no GUI)

This example shows how DataRacks now properly occupy multiple tiles
when placed in a room, with collision detection and bounds checking.
'''

import sys
sys.path.insert(0, 'src')

from room import Room
from datarack import DataRack


def main():
    print("=" * 60)
    print("Multi-Tile DataRack Placement Example")
    print("=" * 60)
    
    # Create a 10x10 tile room
    room = Room(room_id="DC-MAIN", num_tiles_x=10, num_tiles_y=10, height=3.0)
    print(f"\nCreated room: {room.room_id}")
    print(f"  Dimensions: {room.num_tiles_x}x{room.num_tiles_y} tiles")
    print(f"  Physical size: {room.length}m x {room.width}m x {room.height}m")
    print(f"  Total area: {room.area:.2f} m²")
    
    # Place a standard 2x2 rack
    print("\n" + "-" * 60)
    rack1 = DataRack("RACK-01", 2, 2, 42, width_tiles=2, depth_tiles=2)
    result1 = room.add_data_rack(rack1)
    print(f"Placing {rack1}")
    print(f"  Success: {result1}")
    print(f"  Tiles occupied: {rack1.get_tile_footprint()}")
    
    # Place a large 3x2 rack
    print("\n" + "-" * 60)
    rack2 = DataRack("RACK-02", 5, 3, 45, width_tiles=3, depth_tiles=2)
    result2 = room.add_data_rack(rack2)
    print(f"Placing {rack2}")
    print(f"  Success: {result2}")
    print(f"  Tiles occupied: {rack2.get_tile_footprint()}")
    
    # Try to place an overlapping rack (should fail)
    print("\n" + "-" * 60)
    rack3 = DataRack("RACK-03", 3, 3, 40, width_tiles=2, depth_tiles=2)
    result3 = room.add_data_rack(rack3)
    print(f"Attempting to place {rack3}")
    print(f"  Success: {result3} (Expected False - overlaps with RACK-01)")
    
    # Try to place a rack out of bounds (should fail)
    print("\n" + "-" * 60)
    rack4 = DataRack("RACK-04", 9, 9, 40, width_tiles=2, depth_tiles=2)
    result4 = room.add_data_rack(rack4)
    print(f"Attempting to place {rack4}")
    print(f"  Success: {result4} (Expected False - out of bounds)")
    
    # Place a single-tile rack
    print("\n" + "-" * 60)
    rack5 = DataRack("RACK-05", 0, 0, 20, width_tiles=1, depth_tiles=1)
    result5 = room.add_data_rack(rack5)
    print(f"Placing {rack5}")
    print(f"  Success: {result5}")
    print(f"  Tiles occupied: {rack5.get_tile_footprint()}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Room Summary")
    print("=" * 60)
    print(f"Total racks placed: {len(room.data_racks)}")
    print(f"Occupied tiles: {len(room.get_occupied_tiles())} / {room.num_tiles_x * room.num_tiles_y}")
    print(f"Unoccupied tiles: {len(room.get_unoccupied_tiles())}")
    
    print("\nRack Details:")
    for rack in room.data_racks:
        info = rack.get_rack_info()
        print(f"  {info['rack_id']}: {info['width_tiles']}x{info['depth_tiles']} tiles, "
              f"{info['rack_units']}U, {info['rack_height_meters']:.2f}m tall")


if __name__ == "__main__":
    main()
