'''
@file: test_ladder.py
@author: airside-tech

Unit tests for the Ladder class
'''

import pytest
from ladder import Ladder, Section


class TestLadderCreation:
    """Test Ladder initialization"""
    
    def test_ladder_creation(self):
        """Test creating a basic ladder"""
        ladder = Ladder(ladder_id="LAD001")
        
        assert ladder.ladder_id == "LAD001"
        assert isinstance(ladder.sections, list)
        assert len(ladder.sections) == 0

    def test_ladder_with_different_ids(self):
        """Test creating ladders with different IDs"""
        ladder1 = Ladder("LAD_NORTH_01")
        ladder2 = Ladder("LAD_SOUTH_02")
        
        assert ladder1.ladder_id == "LAD_NORTH_01"
        assert ladder2.ladder_id == "LAD_SOUTH_02"
        assert ladder1.ladder_id != ladder2.ladder_id


class TestLadderSections:
    """Test Ladder section management"""
    
    def test_add_single_section(self):
        """Test adding a single section to ladder"""
        ladder = Ladder("LAD002")
        section = Section("SEC001", 0.0, 0.0, 1.5, "horizontal")
        
        ladder.add_section(section)
        
        assert len(ladder.sections) == 1
        assert ladder.sections[0] == section

    def test_remove_section(self):
        """Test removing a section from ladder"""
        ladder = Ladder("LAD018")
        section1 = Section("SEC001", 0.0, 0.0, 1.5, "horizontal")
        section2 = Section("SEC002", 1.5, 0.0, 1.5, "horizontal")
        
        ladder.add_section(section1)
        ladder.add_section(section2)
        
        assert len(ladder.sections) == 2
        
        ladder.remove_section("SEC001")
        
        assert len(ladder.sections) == 1
        assert ladder.sections[0] == section2
        

    def test_add_multiple_sections(self):
        """Test adding multiple sections to ladder"""
        ladder = Ladder("LAD003")
        section1 = Section("SEC001", 0.0, 0.0, 1.5, "horizontal")
        section2 = Section("SEC002", 1.5, 0.0, 1.5, "horizontal")
        section3 = Section("SEC003", 3.0, 0.0, 1.5, "vertical")
        
        ladder.add_section(section1)
        ladder.add_section(section2)
        ladder.add_section(section3)
        
        assert len(ladder.sections) == 3
        assert ladder.sections[0].section_id == "SEC001"
        assert ladder.sections[1].section_id == "SEC002"
        assert ladder.sections[2].section_id == "SEC003"

    def test_add_sections_maintains_order(self):
        """Test that sections maintain insertion order"""
        ladder = Ladder("LAD004")
        sections = [
            Section(f"SEC{i:03d}", 0.0, 0.0, 1.5, "horizontal")
            for i in range(1, 6)
        ]
        
        for section in sections:
            ladder.add_section(section)
        
        for i, section in enumerate(ladder.sections):
            assert section.section_id == f"SEC{i+1:03d}"


class TestLadderTotalLength:
    """Test Ladder total_length property"""
    
    def test_total_length_empty_ladder(self):
        """Test total length of ladder with no sections"""
        ladder = Ladder("LAD005")
        
        assert ladder.total_length == 0.0

    def test_total_length_single_section(self):
        """Test total length with single section"""
        ladder = Ladder("LAD006")
        section = Section("SEC001", 0.0, 0.0, 1.5, "horizontal")
        ladder.add_section(section)
        
        assert ladder.total_length == 1.5

    def test_total_length_multiple_sections(self):
        """Test total length with multiple sections"""
        ladder = Ladder("LAD007")
        ladder.add_section(Section("SEC001", 0.0, 0.0, 1.5, "horizontal"))
        ladder.add_section(Section("SEC002", 1.5, 0.0, 2.0, "horizontal"))
        ladder.add_section(Section("SEC003", 3.5, 0.0, 1.0, "vertical"))
        
        assert ladder.total_length == 4.5

    def test_total_length_with_various_lengths(self):
        """Test total length calculation with various section lengths"""
        ladder = Ladder("LAD008")
        lengths = [0.5, 1.0, 1.5, 2.0, 0.75]
        
        for i, length in enumerate(lengths):
            section = Section(f"SEC{i:03d}", 0.0, 0.0, length, "horizontal")
            ladder.add_section(section)
        
        expected_total = sum(lengths)
        assert ladder.total_length == expected_total

    def test_total_length_updates_after_adding_sections(self):
        """Test that total_length updates dynamically"""
        ladder = Ladder("LAD009")
        
        assert ladder.total_length == 0.0
        
        ladder.add_section(Section("SEC001", 0.0, 0.0, 1.0, "horizontal"))
        assert ladder.total_length == 1.0
        
        ladder.add_section(Section("SEC002", 1.0, 0.0, 2.0, "horizontal"))
        assert ladder.total_length == 3.0
        
        ladder.add_section(Section("SEC003", 3.0, 0.0, 0.5, "horizontal"))
        assert ladder.total_length == 3.5


class TestLadderOrientations:
    """Test Ladder with different section orientations"""
    
    def test_ladder_with_horizontal_sections(self):
        """Test ladder composed of horizontal sections"""
        ladder = Ladder("LAD010")
        for i in range(3):
            section = Section(
                f"SEC{i:03d}", float(i*1.5), 0.0, 1.5, "horizontal"
            )
            ladder.add_section(section)
        
        assert all(s.orientation == "horizontal" for s in ladder.sections)
        assert ladder.total_length == 4.5

    def test_ladder_with_vertical_sections(self):
        """Test ladder composed of vertical sections"""
        ladder = Ladder("LAD011")
        for i in range(3):
            section = Section(
                f"SEC{i:03d}", 0.0, float(i*1.5), 1.5, "vertical"
            )
            ladder.add_section(section)
        
        assert all(s.orientation == "vertical" for s in ladder.sections)
        assert ladder.total_length == 4.5

    def test_ladder_with_mixed_orientations(self):
        """Test ladder with both horizontal and vertical sections"""
        ladder = Ladder("LAD012")
        ladder.add_section(Section("SEC001", 0.0, 0.0, 1.5, "horizontal"))
        ladder.add_section(Section("SEC002", 1.5, 0.0, 2.0, "vertical"))
        ladder.add_section(Section("SEC003", 1.5, 2.0, 1.5, "horizontal"))
        
        orientations = [s.orientation for s in ladder.sections]
        assert "horizontal" in orientations
        assert "vertical" in orientations
        assert ladder.total_length == 5.0


class TestLadderWithCurvedSections:
    """Test Ladder with curved sections"""
    
    def test_ladder_with_bent_sections(self):
        """Test ladder containing bent sections"""
        ladder = Ladder("LAD013")
        ladder.add_section(
            Section("SEC001", 0.0, 0.0, 1.5, "horizontal", bend_degree=0.0)
        )
        ladder.add_section(
            Section("SEC002", 1.5, 0.0, 1.5, "horizontal", bend_degree=15.0)
        )
        ladder.add_section(
            Section("SEC003", 3.0, 0.0, 1.5, "horizontal", bend_degree=-10.0)
        )
        
        bend_degrees = [s.curved_degree for s in ladder.sections]
        assert 0.0 in bend_degrees
        assert 15.0 in bend_degrees
        assert -10.0 in bend_degrees

    def test_ladder_total_length_includes_bent_sections(self):
        """Test that total_length includes bent sections"""
        ladder = Ladder("LAD014")
        ladder.add_section(Section("SEC001", 0.0, 0.0, 2.0, "horizontal"))
        ladder.add_section(
            Section("SEC002", 2.0, 0.0, 1.5, "horizontal", bend_degree=25.0)
        )
        
        assert ladder.total_length == 3.5


class TestLadderWithDifferentMaterials:
    """Test Ladder with different materials"""
    
    def test_ladder_with_aluminum_sections(self):
        """Test ladder with aluminum sections"""
        ladder = Ladder("LAD015")
        ladder.add_section(Section("SEC001", 0.0, 0.0, 1.5, "horizontal"))
        ladder.add_section(Section("SEC002", 1.5, 0.0, 1.5, "horizontal"))
        
        assert all(s.material == "aluminum" for s in ladder.sections)

    def test_ladder_with_steel_sections(self):
        """Test ladder with steel sections"""
        ladder = Ladder("LAD016")
        ladder.add_section(
            Section("SEC001", 0.0, 0.0, 1.5, "horizontal", material="steel")
        )
        ladder.add_section(
            Section("SEC002", 1.5, 0.0, 1.5, "horizontal", material="steel")
        )
        
        assert all(s.material == "steel" for s in ladder.sections)

    def test_ladder_with_mixed_materials(self):
        """Test ladder with mixed materials"""
        ladder = Ladder("LAD017")
        ladder.add_section(Section("SEC001", 0.0, 0.0, 1.5, "horizontal"))
        ladder.add_section(
            Section("SEC002", 1.5, 0.0, 1.5, "horizontal", material="steel")
        )
        
        materials = [s.material for s in ladder.sections]
        assert "aluminum" in materials
        assert "steel" in materials
