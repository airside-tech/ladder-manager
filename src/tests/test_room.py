'''
@file: test_room.py

Unit tests for the Room class and DataRack integration
'''

import pytest
from room import Room
from datarack import DataRack


class TestRoomCreation:
    """Test Room initialization"""

    def test_room_creation_basic(self):
        room = Room(room_id="DC01", num_tiles_x=10, num_tiles_y=8, height=3.0)
        assert room.room_id == "DC01"
        assert room.num_tiles_x == 10
        assert room.num_tiles_y == 8
        assert room.height == 3.0
        assert room.tile_size_xy == 0.6
        assert len(room.data_racks) == 0

    def test_room_tile_grid_initialized_empty(self):
        room = Room("DC02", 5, 4, 2.5)
        assert len(room.tile_grid) == 5
        assert len(room.tile_grid[0]) == 4
        # All tiles should start unoccupied
        for x in range(5):
            for y in range(4):
                assert room.tile_grid[x][y] == False


class TestRoomProperties:
    """Test Room calculated properties"""

    def test_room_area(self):
        room = Room("DC03", 10, 8, 3.0, tile_size_xy=0.6)
        expected_area = 10 * 0.6 * 8 * 0.6
        assert pytest.approx(room.area, rel=1e-6) == expected_area

    def test_room_volume(self):
        room = Room("DC04", 10, 8, 3.0, tile_size_xy=0.6)
        expected_volume = 10 * 0.6 * 8 * 0.6 * 3.0
        assert pytest.approx(room.volume, rel=1e-6) == expected_volume


class TestDataRackPlacement:
    """Test adding DataRacks to rooms and multi-tile occupancy"""

    def test_add_single_tile_rack(self):
        room = Room("DC05", 10, 10, 3.0)
        rack = DataRack("RACK01", 2, 3, 42, width_tiles=1, depth_tiles=1)
        
        result = room.add_data_rack(rack)
        
        assert result == True
        assert len(room.data_racks) == 1
        assert room.data_racks[0] == rack
        assert room.is_tile_occupied(2, 3) == True

    def test_add_multi_tile_rack_2x2(self):
        room = Room("DC06", 10, 10, 3.0)
        rack = DataRack("RACK02", 4, 5, 42, width_tiles=2, depth_tiles=2)
        
        result = room.add_data_rack(rack)
        
        assert result == True
        assert len(room.data_racks) == 1
        # Check all 4 tiles are occupied
        assert room.is_tile_occupied(4, 5) == True
        assert room.is_tile_occupied(5, 5) == True
        assert room.is_tile_occupied(4, 6) == True
        assert room.is_tile_occupied(5, 6) == True

    def test_add_multi_tile_rack_3x1(self):
        room = Room("DC07", 10, 10, 3.0)
        rack = DataRack("RACK03", 1, 1, 20, width_tiles=3, depth_tiles=1)
        
        result = room.add_data_rack(rack)
        
        assert result == True
        # Check all 3 tiles in a row are occupied
        assert room.is_tile_occupied(1, 1) == True
        assert room.is_tile_occupied(2, 1) == True
        assert room.is_tile_occupied(3, 1) == True

    def test_add_rack_out_of_bounds_fails(self):
        room = Room("DC08", 5, 5, 3.0)
        # Rack at (4, 4) with 2x2 footprint would go out of bounds
        rack = DataRack("RACK04", 4, 4, 42, width_tiles=2, depth_tiles=2)
        
        result = room.add_data_rack(rack)
        
        assert result == False
        assert len(room.data_racks) == 0

    def test_add_rack_overlapping_fails(self):
        room = Room("DC09", 10, 10, 3.0)
        rack1 = DataRack("RACK05", 3, 3, 42, width_tiles=2, depth_tiles=2)
        rack2 = DataRack("RACK06", 4, 4, 42, width_tiles=2, depth_tiles=2)
        
        result1 = room.add_data_rack(rack1)
        result2 = room.add_data_rack(rack2)
        
        assert result1 == True
        assert result2 == False  # Overlaps with rack1
        assert len(room.data_racks) == 1

    def test_add_multiple_non_overlapping_racks(self):
        room = Room("DC10", 10, 10, 3.0)
        rack1 = DataRack("RACK07", 0, 0, 42, width_tiles=2, depth_tiles=2)
        rack2 = DataRack("RACK08", 3, 0, 42, width_tiles=2, depth_tiles=2)
        rack3 = DataRack("RACK09", 6, 0, 42, width_tiles=2, depth_tiles=2)
        
        result1 = room.add_data_rack(rack1)
        result2 = room.add_data_rack(rack2)
        result3 = room.add_data_rack(rack3)
        
        assert result1 == True
        assert result2 == True
        assert result3 == True
        assert len(room.data_racks) == 3


class TestTileOccupancy:
    """Test tile occupancy queries"""

    def test_get_occupied_tiles_empty_room(self):
        room = Room("DC11", 5, 5, 3.0)
        occupied = room.get_occupied_tiles()
        assert len(occupied) == 0

    def test_get_occupied_tiles_after_rack_placement(self):
        room = Room("DC12", 10, 10, 3.0)
        rack = DataRack("RACK10", 2, 3, 42, width_tiles=2, depth_tiles=3)
        room.add_data_rack(rack)
        
        occupied = room.get_occupied_tiles()
        expected = [(2, 3), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5)]
        
        assert len(occupied) == 6
        assert set(occupied) == set(expected)

    def test_get_unoccupied_tiles(self):
        room = Room("DC13", 3, 3, 3.0)
        rack = DataRack("RACK11", 0, 0, 42, width_tiles=1, depth_tiles=1)
        room.add_data_rack(rack)
        
        unoccupied = room.get_unoccupied_tiles()
        
        assert len(unoccupied) == 8  # 9 total - 1 occupied
        assert (0, 0) not in unoccupied
