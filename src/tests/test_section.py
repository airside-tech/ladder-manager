'''
@file: test_section.py
@author: airside-tech

Unit tests for the Section class
'''

import pytest
from ladder import Section


class TestSectionCreation:
    """Test Section initialization and basic properties"""
    
    def test_section_creation_with_defaults(self):
        """Test creating a section with default parameters"""
        section = Section(
            section_id="SEC001",
            x_coord=0.0,
            y_coord=0.0,
            length=1.5,
            orientation="horizontal"
        )
        
        assert section.section_id == "SEC001"
        assert section.length == 1.5
        assert section.orientation == "horizontal"
        assert section.material == "aluminum"
        assert section.width == 30.0
        assert section.curved_degree == 0.0
        assert section.x_coord == 0.0
        assert section.y_coord == 0.0

    def test_section_creation_with_all_parameters(self):
        """Test creating a section with all custom parameters"""
        section = Section(
            section_id="SEC002",
            x_coord=2.0,
            y_coord=3.5,
            length=2.0,
            orientation="vertical",
            bend_degree=15.0,
            width=40.0,
            material="steel"
        )
        
        assert section.section_id == "SEC002"
        assert section.length == 2.0
        assert section.orientation == "vertical"
        assert section.material == "steel"
        assert section.width == 40.0
        assert section.curved_degree == 15.0
        assert section.x_coord == 2.0
        assert section.y_coord == 3.5

    def test_section_positive_bend_degree(self):
        """Test section with positive bend degree (right bend)"""
        section = Section(
            section_id="SEC003",
            x_coord=0.0,
            y_coord=0.0,
            length=1.0,
            orientation="horizontal",
            bend_degree=25.0
        )
        
        assert section.curved_degree == 25.0

    def test_section_negative_bend_degree(self):
        """Test section with negative bend degree (left bend)"""
        section = Section(
            section_id="SEC004",
            x_coord=0.0,
            y_coord=0.0,
            length=1.0,
            orientation="horizontal",
            bend_degree=-15.0
        )
        
        assert section.curved_degree == -15.0

    def test_section_orientation_values(self):
        """Test different orientation values"""
        horizontal = Section("H001", 0.0, 0.0, 1.5, "horizontal")
        vertical = Section("V001", 0.0, 0.0, 1.5, "vertical")
        
        assert horizontal.orientation == "horizontal"
        assert vertical.orientation == "vertical"


class TestSectionCoordinates:
    """Test Section coordinate handling"""
    
    def test_section_coordinates_assignment(self):
        """Test setting and reading section coordinates"""
        section = Section("SEC005", 5.0, 10.0, 1.5, "horizontal")
        
        assert section.x_coord == 5.0
        assert section.y_coord == 10.0

    def test_section_zero_coordinates(self):
        """Test section starting at origin"""
        section = Section("SEC006", 0.0, 0.0, 1.5, "horizontal")
        
        assert section.x_coord == 0.0
        assert section.y_coord == 0.0

    def test_section_negative_coordinates(self):
        """Test section with negative coordinates"""
        section = Section("SEC007", -2.5, -3.5, 1.5, "horizontal")
        
        assert section.x_coord == -2.5
        assert section.y_coord == -3.5


class TestSectionMaterials:
    """Test Section material handling"""
    
    def test_section_default_material(self):
        """Test default material is aluminum"""
        section = Section("SEC008", 0.0, 0.0, 1.5, "horizontal")
        
        assert section.material == "aluminum"

    def test_section_steel_material(self):
        """Test steel material assignment"""
        section = Section(
            "SEC009", 0.0, 0.0, 1.5, "horizontal", material="steel"
        )
        
        assert section.material == "steel"

    def test_section_custom_material(self):
        """Test custom material assignment"""
        section = Section(
            "SEC010", 0.0, 0.0, 1.5, "horizontal", material="galvanized_steel"
        )
        
        assert section.material == "galvanized_steel"


class TestSectionDimensions:
    """Test Section dimension attributes"""
    
    def test_section_length_values(self):
        """Test various length values"""
        short = Section("S001", 0.0, 0.0, 0.5, "horizontal")
        medium = Section("M001", 0.0, 0.0, 1.5, "horizontal")
        long = Section("L001", 0.0, 0.0, 3.0, "horizontal")
        
        assert short.length == 0.5
        assert medium.length == 1.5
        assert long.length == 3.0

    def test_section_default_width(self):
        """Test default width is 30 cm"""
        section = Section("SEC011", 0.0, 0.0, 1.5, "horizontal")
        
        assert section.width == 30.0

    def test_section_custom_width(self):
        """Test custom width assignment"""
        section = Section(
            "SEC012", 0.0, 0.0, 1.5, "horizontal", width=50.0
        )
        
        assert section.width == 50.0
