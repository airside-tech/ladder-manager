'''
@file: test_datarack.py

Unit tests for the DataRack class
'''

import pytest
from datarack import DataRack


class TestDataRackCreation:
    """Test DataRack initialization and basic properties"""

    def test_datarack_creation_basic(self):
        rack = DataRack(rack_id="RACK01", position_x=2, position_y=3, rack_units=42)

        assert rack.rack_id == "RACK01"
        assert rack.position_x == 2
        assert rack.position_y == 3
        assert rack.rack_units == 42
        # Derived values
        assert pytest.approx(rack.rack_height_meters, rel=1e-6) == 42 * 0.04445
        assert pytest.approx(rack.rack_height_inches, rel=1e-6) == 42 * 1.75
        assert pytest.approx(rack.rack_weight_kg_estimated, rel=1e-6) == 42 * 4.5

    def test_datarack_creation_zero_units(self):
        rack = DataRack("RACKZERO", 0, 0, 0)
        assert rack.rack_units == 0
        assert rack.get_rack_height_meters() == 0.0
        assert rack.get_rack_weight_estimated() == 0.0


class TestDataRackGetters:
    """Test getter methods"""

    def test_get_rack_id(self):
        rack = DataRack("RACK02", 1, 1, 10)
        assert rack.get_rack_id() == "RACK02"

    def test_get_rack_position(self):
        rack = DataRack("RACK03", 5, 7, 20)
        assert rack.get_rack_position() == (5, 7)

    def test_get_rack_height_meters(self):
        rack = DataRack("RACK04", 0, 0, 5)
        assert pytest.approx(rack.get_rack_height_meters(), rel=1e-6) == 5 * 0.04445

    def test_get_rack_weight_estimated(self):
        rack = DataRack("RACK05", 0, 0, 8)
        assert pytest.approx(rack.get_rack_weight_estimated(), rel=1e-6) == 8 * 4.5

    def test_get_rack_units(self):
        rack = DataRack("RACK06", 3, 4, 12)
        assert rack.get_rack_units() == 12


class TestDataRackSetters:
    """Test setter methods and their side effects on derived properties"""

    def test_set_rack_units_updates_derived(self):
        rack = DataRack("RACK07", 0, 0, 10)
        rack.set_rack_units(20)
        assert rack.rack_units == 20
        assert pytest.approx(rack.rack_height_meters, rel=1e-6) == 20 * 0.04445
        assert pytest.approx(rack.rack_height_inches, rel=1e-6) == 20 * 1.75
        assert pytest.approx(rack.rack_weight_kg_estimated, rel=1e-6) == 20 * 4.5

    def test_set_rack_position(self):
        rack = DataRack("RACK08", 2, 2, 5)
        rack.set_rack_position(10, 15)
        assert rack.position_x == 10
        assert rack.position_y == 15
        assert rack.get_rack_position() == (10, 15)


class TestDataRackTileFootprint:
    """Test tile footprint calculation"""

    def test_get_tile_footprint_single_tile(self):
        rack = DataRack("RACK11", 2, 3, 42, width_tiles=1, depth_tiles=1)
        footprint = rack.get_tile_footprint()
        assert footprint == [(2, 3)]

    def test_get_tile_footprint_2x2(self):
        rack = DataRack("RACK12", 5, 6, 42, width_tiles=2, depth_tiles=2)
        footprint = rack.get_tile_footprint()
        expected = [(5, 6), (5, 7), (6, 6), (6, 7)]
        assert set(footprint) == set(expected)

    def test_get_tile_footprint_3x1(self):
        rack = DataRack("RACK13", 1, 1, 20, width_tiles=3, depth_tiles=1)
        footprint = rack.get_tile_footprint()
        expected = [(1, 1), (2, 1), (3, 1)]
        assert footprint == expected

    def test_get_tile_footprint_1x4(self):
        rack = DataRack("RACK14", 0, 0, 20, width_tiles=1, depth_tiles=4)
        footprint = rack.get_tile_footprint()
        expected = [(0, 0), (0, 1), (0, 2), (0, 3)]
        assert footprint == expected

    def test_default_footprint_is_1x1(self):
        rack = DataRack("RACK15", 10, 10, 42)
        footprint = rack.get_tile_footprint()
        assert footprint == [(10, 10)]
        assert rack.width_tiles == 1
        assert rack.depth_tiles == 1


class TestDataRackInfoAndRepr:
    """Test info dict and representation"""

    def test_get_rack_info(self):
        rack = DataRack("RACK09", 1, 2, 3)
        info = rack.get_rack_info()
        assert info["rack_id"] == "RACK09"
        assert info["position_x"] == 1
        assert info["position_y"] == 2
        assert info["rack_units"] == 3
        assert info["width_tiles"] == 1
        assert info["depth_tiles"] == 1
        assert pytest.approx(info["rack_height_meters"], rel=1e-6) == 3 * 0.04445
        assert pytest.approx(info["rack_height_inches"], rel=1e-6) == 3 * 1.75
        assert pytest.approx(info["rack_weight_kg_estimated"], rel=1e-6) == 3 * 4.5

    def test_get_rack_info_with_custom_footprint(self):
        rack = DataRack("RACK16", 5, 5, 20, width_tiles=2, depth_tiles=3)
        info = rack.get_rack_info()
        assert info["width_tiles"] == 2
        assert info["depth_tiles"] == 3

    def test_repr_contains_key_fields(self):
        rack = DataRack("RACK10", 9, 8, 7)
        rep = repr(rack)
        assert "DataRack(" in rep
        assert "RACK10" in rep
        assert "position=(9, 8)" in rep
        assert "rack_units=7" in rep
        assert "footprint=" in rep
