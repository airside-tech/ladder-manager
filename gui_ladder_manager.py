#!/usr/bin/env python3
'''
GUI for Cable Ladder Manager using pygame

This application provides a visual interface for:
- Viewing a room's tile grid with data racks
- Placing cable ladder segments
- Adding new data racks
- Managing the data center layout

Controls:
- Left Click: Place ladder segment start/end point
- 'R' key: Add new data rack (2x2)
- 'L' key: Toggle ladder placement mode
- 'C' key: Clear current ladder segment
- 'ESC' key: Exit
'''

import sys
import os
sys.path.insert(0, 'src')

import pygame
from room import Room
from datarack import DataRack
from ladder import Ladder, Section
from obstacle import Obstacle
import math

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (240, 240, 240)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 50, 150)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (205, 133, 63)

# Window settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
BASE_TILE_SIZE = 50  # Base pixels per tile (before zoom)
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50


class LadderManagerGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Cable Ladder Manager")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Zoom settings
        self.zoom_level = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        self.zoom_step = 0.1
        
        # Create larger room (25x20 tiles to provide more space)
        self.room = Room(room_id="DC-MAIN", num_tiles_x=25, num_tiles_y=20, height=3.0)
        
        # Ladder management
        self.ladders = []
        self.current_ladder = None
        self.ladder_start_point = None
        self.ladder_mode = False
        self.selected_section = None  # For selecting and deleting sections
        
        # UI state
        self.selected_tile = None
        self.hover_tile = None
        self.obstacle_mode = False  # Toggle for placing obstacles
        self.placement_mode = "rack"  # "rack" or "obstacle"
        self.show_help = False  # Toggle help overlay with H key
        
        # Pre-populate with data racks in three rows
        self.populate_initial_racks()
        
        self.running = True
    
    @property
    def TILE_SIZE(self):
        """Get current tile size based on zoom level"""
        return int(BASE_TILE_SIZE * self.zoom_level)

    # ----------------------------
    # Initialization helpers
    # ----------------------------

    def populate_initial_racks(self):
        """Pre-populate three rows with 2x2 data racks (42U)"""
        rack_id = 1
        # Three rows: y positions 2, 7, 12
        for row in [2, 7, 12]:
            # Place racks with 1-tile gap between them
            for x in range(0, 25, 3):  # 0, 3, 6, 9, 12, 15, 18, 21
                if x + 1 < self.room.num_tiles_x:  # Ensure rack fits
                    rack = DataRack(
                        rack_id=f"RACK-{rack_id:02d}",
                        position_x=x,
                        position_y=row,
                        rack_units=42,
                        width_tiles=2,
                        depth_tiles=2
                    )
                    self.room.add_data_rack(rack)
                    rack_id += 1

    def get_tile_from_mouse(self, mouse_pos):
        """Convert mouse position to tile coordinates"""
        x, y = mouse_pos
        tile_x = (x - GRID_OFFSET_X) // self.TILE_SIZE
        tile_y = (y - GRID_OFFSET_Y) // self.TILE_SIZE
        
        if 0 <= tile_x < self.room.num_tiles_x and 0 <= tile_y < self.room.num_tiles_y:
            return (int(tile_x), int(tile_y))
        return None

    def get_tile_center(self, tile_x, tile_y):
        """Get pixel coordinates of tile center"""
        x = GRID_OFFSET_X + tile_x * self.TILE_SIZE + self.TILE_SIZE // 2
        y = GRID_OFFSET_Y + tile_y * self.TILE_SIZE + self.TILE_SIZE // 2
        return (x, y)

    def draw_grid(self):
        """Draw the tile grid with dotted lines"""
        # Draw tiles
        for x in range(self.room.num_tiles_x):
            for y in range(self.room.num_tiles_y):
                rect = pygame.Rect(
                    GRID_OFFSET_X + x * self.TILE_SIZE,
                    GRID_OFFSET_Y + y * self.TILE_SIZE,
                    self.TILE_SIZE,
                    self.TILE_SIZE
                )
                
                # Fill tile background
                if self.hover_tile == (x, y):
                    pygame.draw.rect(self.screen, LIGHT_GRAY, rect)
                else:
                    pygame.draw.rect(self.screen, WHITE, rect)
                
                # Draw dotted border
                self.draw_dotted_rect(rect, GRAY, 1)

        # Overlay occupied tiles for clarity
        self.draw_occupied_overlay()

    def draw_dotted_rect(self, rect, color, width):
        """Draw a rectangle with dotted lines"""
        dash_length = 4
        gap_length = 4
        
        # Top line
        self.draw_dotted_line(
            (rect.left, rect.top),
            (rect.right, rect.top),
            color, width, dash_length, gap_length
        )
        # Bottom line
        self.draw_dotted_line(
            (rect.left, rect.bottom),
            (rect.right, rect.bottom),
            color, width, dash_length, gap_length
        )
        # Left line
        self.draw_dotted_line(
            (rect.left, rect.top),
            (rect.left, rect.bottom),
            color, width, dash_length, gap_length
        )
        # Right line
        self.draw_dotted_line(
            (rect.right, rect.top),
            (rect.right, rect.bottom),
            color, width, dash_length, gap_length
        )

    def draw_dotted_line(self, start, end, color, width, dash, gap):
        """Draw a dotted line between two points"""
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
        
        dx = dx / distance
        dy = dy / distance
        
        current_distance = 0
        while current_distance < distance:
            start_x = x1 + dx * current_distance
            start_y = y1 + dy * current_distance
            end_distance = min(current_distance + dash, distance)
            end_x = x1 + dx * end_distance
            end_y = y1 + dy * end_distance
            
            pygame.draw.line(
                self.screen, color,
                (int(start_x), int(start_y)),
                (int(end_x), int(end_y)),
                width
            )
            
            current_distance += dash + gap

    def draw_racks(self):
        """Draw all data racks"""
        for rack in self.room.data_racks:
            footprint = rack.get_tile_footprint()
            
            # Calculate rack rectangle
            min_x = min(t[0] for t in footprint)
            min_y = min(t[1] for t in footprint)
            max_x = max(t[0] for t in footprint)
            max_y = max(t[1] for t in footprint)
            
            rect = pygame.Rect(
                GRID_OFFSET_X + min_x * self.TILE_SIZE + 2,
                GRID_OFFSET_Y + min_y * self.TILE_SIZE + 2,
                (max_x - min_x + 1) * self.TILE_SIZE - 4,
                (max_y - min_y + 1) * self.TILE_SIZE - 4
            )
            
            # Draw rack
            pygame.draw.rect(self.screen, DARK_BLUE, rect)
            pygame.draw.rect(self.screen, BLUE, rect, 2)
            
            # Draw rack label
            label = self.small_font.render(rack.rack_id, True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

        # Draw a hover preview for a 2x2 rack (green if placeable, red if blocked)
        self.draw_hover_rack_preview()

    def draw_obstacles(self):
        """Draw all obstacles"""
        for obstacle in self.room.obstacles:
            footprint = obstacle.get_tile_footprint()
            
            # Calculate obstacle rectangle
            min_x = min(t[0] for t in footprint)
            min_y = min(t[1] for t in footprint)
            max_x = max(t[0] for t in footprint)
            max_y = max(t[1] for t in footprint)
            
            rect = pygame.Rect(
                GRID_OFFSET_X + min_x * self.TILE_SIZE + 2,
                GRID_OFFSET_Y + min_y * self.TILE_SIZE + 2,
                (max_x - min_x + 1) * self.TILE_SIZE - 4,
                (max_y - min_y + 1) * self.TILE_SIZE - 4
            )
            
            # Draw obstacle with brown/hazard pattern
            pygame.draw.rect(self.screen, DARK_BROWN, rect)
            pygame.draw.rect(self.screen, BROWN, rect, 3)
            
            # Draw diagonal stripes for obstacle pattern
            stripe_spacing = 8
            for i in range(0, rect.width + rect.height, stripe_spacing):
                start_x = rect.left + i
                start_y = rect.top
                end_x = rect.left
                end_y = rect.top + i
                
                if start_x > rect.right:
                    start_x = rect.right
                    start_y = rect.top + (i - rect.width)
                
                if end_y > rect.bottom:
                    end_y = rect.bottom
                    end_x = rect.left + (i - rect.height)
                
                pygame.draw.line(self.screen, LIGHT_BROWN, (start_x, start_y), (end_x, end_y), 2)
            
            # Draw obstacle label
            label = self.small_font.render(obstacle.obstacle_id, True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

        # Draw hover preview for obstacle placement
        self.draw_hover_obstacle_preview()


    def draw_ladders(self):
        """Draw all ladder segments with width visualization"""
        for ladder in self.ladders:
            for section in ladder.sections:
                start = self.get_tile_center(int(section.x_coord), int(section.y_coord))
                
                # Calculate end point based on orientation and length
                if section.orientation == "horizontal":
                    end = (start[0] + int(section.length * self.TILE_SIZE), start[1])
                else:  # vertical
                    end = (start[0], start[1] + int(section.length * self.TILE_SIZE))
                
                # Calculate line width based on ladder width (cm to pixels)
                # Standard widths: 30cm, 60cm, 90cm, 120cm
                # Map to reasonable pixel widths: 4, 8, 12, 16
                ladder_width_cm = getattr(section, 'width', 30.0)
                line_width = max(3, int(ladder_width_cm / 10))  # Scale: 30cm -> 3px, 60cm -> 6px, etc.
                
                # Color based on width (capacity indicator)
                if ladder_width_cm <= 30:
                    color = ORANGE  # Small capacity
                elif ladder_width_cm <= 60:
                    color = (255, 200, 0)  # Medium capacity (yellow-orange)
                elif ladder_width_cm <= 90:
                    color = (200, 255, 0)  # Good capacity (yellow-green)
                else:
                    color = GREEN  # High capacity
                
                # Highlight selected section
                if self.selected_section == section:
                    color = YELLOW
                    line_width += 2
                
                # Draw ladder segment as a thick line
                pygame.draw.line(self.screen, color, start, end, line_width)
                
                # Draw borders for better visibility
                if section.orientation == "horizontal":
                    # Top and bottom borders
                    offset = line_width // 2
                    pygame.draw.line(self.screen, DARK_GRAY, 
                                   (start[0], start[1] - offset), 
                                   (end[0], end[1] - offset), 1)
                    pygame.draw.line(self.screen, DARK_GRAY, 
                                   (start[0], start[1] + offset), 
                                   (end[0], end[1] + offset), 1)
                else:
                    # Left and right borders
                    offset = line_width // 2
                    pygame.draw.line(self.screen, DARK_GRAY, 
                                   (start[0] - offset, start[1]), 
                                   (end[0] - offset, end[1]), 1)
                    pygame.draw.line(self.screen, DARK_GRAY, 
                                   (start[0] + offset, start[1]), 
                                   (end[0] + offset, end[1]), 1)
                
                # Draw end points
                pygame.draw.circle(self.screen, RED, start, 4)
                pygame.draw.circle(self.screen, RED, end, 4)
                
                # Draw width label for selected or hovered section
                if self.selected_section == section:
                    mid_x = (start[0] + end[0]) // 2
                    mid_y = (start[1] + end[1]) // 2
                    label = self.small_font.render(f"{int(ladder_width_cm)}cm", True, BLACK)
                    
                    # Background for label
                    label_bg = pygame.Surface((label.get_width() + 4, label.get_height() + 2), pygame.SRCALPHA)
                    label_bg.fill((255, 255, 255, 200))
                    self.screen.blit(label_bg, (mid_x - label.get_width() // 2 - 2, mid_y - label.get_height() // 2 - 1))
                    self.screen.blit(label, (mid_x - label.get_width() // 2, mid_y - label.get_height() // 2))


    def draw_ladder_preview(self, mouse_pos):
        """Draw preview of ladder segment being placed"""
        if self.ladder_start_point and self.ladder_mode:
            start = self.get_tile_center(*self.ladder_start_point)

            # Snap preview to horizontal/vertical based on greater delta
            hover_tile = self.get_tile_from_mouse(mouse_pos)
            if hover_tile is not None:
                sx, sy = self.ladder_start_point
                ex, ey = hover_tile
                if abs(ex - sx) >= abs(ey - sy):
                    snapped_end = self.get_tile_center(ex, sy)
                else:
                    snapped_end = self.get_tile_center(sx, ey)
            else:
                snapped_end = mouse_pos

            # Draw line to snapped end
            pygame.draw.line(self.screen, YELLOW, start, snapped_end, 3)
            pygame.draw.circle(self.screen, YELLOW, start, 6)

    def draw_help_overlay(self):
        """Draw a semi-transparent help overlay when toggled with H key"""
        if not self.show_help:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Help panel in center
        panel_width = 400
        panel_height = 550
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, panel_rect)
        pygame.draw.rect(self.screen, DARK_GRAY, panel_rect, 3)
        
        y_offset = panel_y + 20
        
        # Title
        title = self.font.render("CONTROLS (Press H to close)", True, BLACK)
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, y_offset))
        self.screen.blit(title, title_rect)
        y_offset += 50
        
        # Instructions in two columns
        left_col_x = panel_x + 20
        right_col_x = panel_x + panel_width // 2 + 10
        
        left_instructions = [
            "PLACEMENT:",
            "R: Add Rack (2x2)",
            "B: Add Obstacle (1x1)",
            "T: Toggle Rack/Obstacle",
            "",
            "LADDER:",
            "L: Toggle ladder mode",
            "Click: Start/End point",
            "N: Start new ladder",
            "U: Undo last section",
            "X: Delete last ladder",
            "",
            "SELECTION:",
            "Click: Select section",
            "DEL: Remove selected",
            "C: Clear selection",
        ]
        
        right_instructions = [
            "VIEW:",
            "Mouse Wheel: Zoom",
            "H: Toggle help",
            "",
            "FILE:",
            "S: Save layout",
            "O: Open layout",
            "ESC: Exit",
            "",
            "STATUS:",
            f"Ladder: {'ON' if self.ladder_mode else 'OFF'}",
            f"Mode: {self.placement_mode.upper()}",
            f"Zoom: {self.zoom_level:.1f}x",
            "",
            f"Racks: {len(self.room.data_racks)}",
            f"Obstacles: {len(self.room.obstacles)}",
            f"Ladders: {len(self.ladders)}",
        ]
        
        # Draw left column
        for instruction in left_instructions:
            if instruction.endswith(":"):
                text = self.small_font.render(instruction, True, DARK_BLUE)
            else:
                text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (left_col_x, y_offset))
            y_offset += 22
        
        # Draw right column
        y_offset = panel_y + 70
        for instruction in right_instructions:
            if instruction.endswith(":"):
                text = self.small_font.render(instruction, True, DARK_BLUE)
            else:
                text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (right_col_x, y_offset))
            y_offset += 22
        
        # Draw color legend for ladders at bottom
        y_offset = panel_y + panel_height - 80
        legend_title = self.small_font.render("LADDER WIDTH COLOR CODE:", True, DARK_BLUE)
        self.screen.blit(legend_title, (left_col_x, y_offset))
        y_offset += 25
        
        colors_and_labels = [
            (ORANGE, "30cm (small)"),
            ((255, 200, 0), "60cm (medium)"),
            ((200, 255, 0), "90cm (good)"),
            (GREEN, "120cm+ (high)"),
        ]
        
        for color, label in colors_and_labels:
            pygame.draw.rect(self.screen, color, (left_col_x, y_offset, 20, 12))
            pygame.draw.rect(self.screen, BLACK, (left_col_x, y_offset, 20, 12), 1)
            text = self.small_font.render(label, True, BLACK)
            self.screen.blit(text, (left_col_x + 25, y_offset - 2))
            y_offset += 16

    def add_ladder_segment(self, start_tile, end_tile):
        """Add a new ladder segment between two tiles"""
        x1, y1 = start_tile
        x2, y2 = end_tile
        
        # Determine orientation and length
        if abs(x2 - x1) > abs(y2 - y1):
            orientation = "horizontal"
            length = abs(x2 - x1)
        else:
            orientation = "vertical"
            length = abs(y2 - y1)
        
        # Create ladder if needed
        if not self.current_ladder:
            self.current_ladder = Ladder(f"LAD-{len(self.ladders) + 1:03d}")
            self.ladders.append(self.current_ladder)
        
        # Add section
        section = Section(
            section_id=f"SEC-{len(self.current_ladder.sections) + 1:03d}",
            x_coord=float(min(x1, x2)),
            y_coord=float(min(y1, y2)),
            length=float(length),
            orientation=orientation
        )
        self.current_ladder.add_section(section)

    # ----------------------------
    # Rack helpers and previews
    # ----------------------------

    def can_place_rack(self, tile_x: int, tile_y: int, width_tiles: int = 2, depth_tiles: int = 2) -> bool:
        """Check without modifying room if a rack can be placed at tile."""
        # Bounds check
        if tile_x < 0 or tile_y < 0:
            return False
        if tile_x + width_tiles > self.room.num_tiles_x or tile_y + depth_tiles > self.room.num_tiles_y:
            return False
        # Collision check
        for dx in range(width_tiles):
            for dy in range(depth_tiles):
                if self.room.tile_grid[tile_x + dx][tile_y + dy]:
                    return False
        return True

    def draw_hover_rack_preview(self):
        """Draw a 2x2 rack placement preview at hover tile (green=ok, red=blocked)."""
        if self.hover_tile is None:
            return
        # Don't draw preview while actively placing ladder to reduce clutter
        if self.ladder_mode or self.placement_mode != "rack":
            return

        tx, ty = self.hover_tile
        fits = self.can_place_rack(tx, ty, 2, 2)
        color = (0, 255, 0, 80) if fits else (255, 0, 0, 80)

        # Draw translucent rect over the 2x2 area
        s = pygame.Surface((self.TILE_SIZE * 2 - 4, self.TILE_SIZE * 2 - 4), pygame.SRCALPHA)
        s.fill(color)
        self.screen.blit(
            s,
            (
                GRID_OFFSET_X + tx * self.TILE_SIZE + 2,
                GRID_OFFSET_Y + ty * self.TILE_SIZE + 2,
            ),
        )
    
    def draw_hover_obstacle_preview(self):
        """Draw a 1x1 obstacle placement preview at hover tile (brown=ok, red=blocked)."""
        if self.hover_tile is None:
            return
        # Only draw when in obstacle placement mode
        if self.ladder_mode or self.placement_mode != "obstacle":
            return

        tx, ty = self.hover_tile
        fits = self.can_place_rack(tx, ty, 1, 1)  # Reuse rack placement check for single tile
        color = (139, 69, 19, 120) if fits else (255, 0, 0, 80)  # Brown or red

        # Draw translucent rect over the 1x1 area
        s = pygame.Surface((self.TILE_SIZE - 4, self.TILE_SIZE - 4), pygame.SRCALPHA)
        s.fill(color)
        self.screen.blit(
            s,
            (
                GRID_OFFSET_X + tx * self.TILE_SIZE + 2,
                GRID_OFFSET_Y + ty * self.TILE_SIZE + 2,
            ),
        )

    def add_rack_at_tile(self, tile_x, tile_y):
        """Add a new 2x2 rack at the specified tile"""
        rack = DataRack(
            rack_id=f"RACK-{len(self.room.data_racks) + 1:02d}",
            position_x=tile_x,
            position_y=tile_y,
            rack_units=42,
            width_tiles=2,
            depth_tiles=2
        )
        if self.room.add_data_rack(rack):
            print(f"Added {rack.rack_id} at ({tile_x}, {tile_y})")
        else:
            print(f"Failed to place rack at ({tile_x}, {tile_y}) - tiles occupied or out of bounds")
    
    def add_obstacle_at_tile(self, tile_x, tile_y):
        """Add a new 1x1 obstacle at the specified tile"""
        obstacle = Obstacle(
            obstacle_id=f"OBS-{len(self.room.obstacles) + 1:02d}",
            position_x=tile_x,
            position_y=tile_y,
            width_tiles=1,
            depth_tiles=1,
            height=2.0
        )
        if self.room.add_obstacle(obstacle):
            print(f"Added {obstacle.obstacle_id} at ({tile_x}, {tile_y})")
        else:
            print(f"Failed to place obstacle at ({tile_x}, {tile_y}) - tiles occupied or out of bounds")
    
    def get_section_at_position(self, pixel_pos):
        """Find a ladder section at the given pixel position (for selection)."""
        x, y = pixel_pos
        tolerance = 10  # pixels
        
        for ladder in self.ladders:
            for section in ladder.sections:
                start = self.get_tile_center(int(section.x_coord), int(section.y_coord))
                
                if section.orientation == "horizontal":
                    end = (start[0] + int(section.length * self.TILE_SIZE), start[1])
                    # Check if click is near the horizontal line
                    if (min(start[0], end[0]) - tolerance <= x <= max(start[0], end[0]) + tolerance and
                        abs(y - start[1]) <= tolerance):
                        return section, ladder
                else:  # vertical
                    end = (start[0], start[1] + int(section.length * self.TILE_SIZE))
                    # Check if click is near the vertical line
                    if (abs(x - start[0]) <= tolerance and
                        min(start[1], end[1]) - tolerance <= y <= max(start[1], end[1]) + tolerance):
                        return section, ladder
        
        return None, None

    # ----------------------------
    # Save / Load
    # ----------------------------

    def save_layout(self, path: str = "layout.json"):
        """Save room, racks, obstacles, and ladders to a JSON file."""
        import json

        data = {
            "room": {
                "room_id": self.room.room_id,
                "num_tiles_x": self.room.num_tiles_x,
                "num_tiles_y": self.room.num_tiles_y,
                "height": self.room.height,
                "tile_size_xy": self.room.tile_size_xy,
            },
            "racks": [
                {
                    "rack_id": r.rack_id,
                    "position_x": r.position_x,
                    "position_y": r.position_y,
                    "rack_units": r.rack_units,
                    "width_tiles": getattr(r, "width_tiles", 1),
                    "depth_tiles": getattr(r, "depth_tiles", 1),
                }
                for r in self.room.data_racks
            ],
            "obstacles": [
                {
                    "obstacle_id": o.obstacle_id,
                    "position_x": o.position_x,
                    "position_y": o.position_y,
                    "width_tiles": getattr(o, "width_tiles", 1),
                    "depth_tiles": getattr(o, "depth_tiles", 1),
                    "height": getattr(o, "height", 1.0),
                }
                for o in self.room.obstacles
            ],
            "ladders": [
                {
                    "ladder_id": ld.ladder_id,
                    "sections": [
                        {
                            "section_id": s.section_id,
                            "x_coord": s.x_coord,
                            "y_coord": s.y_coord,
                            "length": s.length,
                            "orientation": s.orientation,
                            "curved_degree": getattr(s, "curved_degree", 0.0),
                            "width": getattr(s, "width", 30.0),
                            "material": getattr(s, "material", "aluminum"),
                        }
                        for s in ld.sections
                    ],
                }
                for ld in self.ladders
            ],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved layout to {os.path.abspath(path)}")

    def load_layout(self, path: str = "layout.json"):
        """Load room, racks, and ladders from a JSON file."""
        import json
        if not os.path.exists(path):
            print(f"Layout file not found: {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Recreate room
        rd = data["room"]
        self.room = Room(
            room_id=rd["room_id"],
            num_tiles_x=int(rd["num_tiles_x"]),
            num_tiles_y=int(rd["num_tiles_y"]),
            height=float(rd["height"]),
        )
        self.room.tile_size_xy = float(rd.get("tile_size_xy", 0.6))

        # Racks
        self.room.data_racks.clear()
        for r in data.get("racks", []):
            rack = DataRack(
                rack_id=r["rack_id"],
                position_x=int(r["position_x"]),
                position_y=int(r["position_y"]),
                rack_units=int(r["rack_units"]),
                width_tiles=int(r.get("width_tiles", 1)),
                depth_tiles=int(r.get("depth_tiles", 1)),
            )
            # Use add_data_rack to set occupancy
            placed = self.room.add_data_rack(rack)
            if not placed:
                print(f"Warning: could not place rack {rack.rack_id} from file (occupied/out of bounds)")

        # Obstacles
        self.room.obstacles.clear()
        for o in data.get("obstacles", []):
            obstacle = Obstacle(
                obstacle_id=o["obstacle_id"],
                position_x=int(o["position_x"]),
                position_y=int(o["position_y"]),
                width_tiles=int(o.get("width_tiles", 1)),
                depth_tiles=int(o.get("depth_tiles", 1)),
                height=float(o.get("height", 1.0)),
            )
            # Use add_obstacle to set occupancy
            placed = self.room.add_obstacle(obstacle)
            if not placed:
                print(f"Warning: could not place obstacle {obstacle.obstacle_id} from file (occupied/out of bounds)")

        # Ladders
        self.ladders = []
        self.current_ladder = None
        for ld in data.get("ladders", []):
            ladder = Ladder(ld.get("ladder_id", f"LAD-{len(self.ladders)+1:03d}"))
            for s in ld.get("sections", []):
                ladder.add_section(
                    Section(
                        section_id=s.get("section_id", f"SEC-{len(ladder.sections)+1:03d}"),
                        x_coord=float(s["x_coord"]),
                        y_coord=float(s["y_coord"]),
                        length=float(s["length"]),
                        orientation=s["orientation"],
                        bend_degree=float(s.get("curved_degree", 0.0)),
                        width=float(s.get("width", 30.0)),
                        material=s.get("material", "aluminum"),
                    )
                )
            self.ladders.append(ladder)
        print(f"Loaded layout from {os.path.abspath(path)}")

    # ----------------------------
    # Overlays
    # ----------------------------
    def draw_occupied_overlay(self):
        """Light overlay on occupied tiles for quick visual feedback."""
        overlay = pygame.Surface((self.TILE_SIZE - 6, self.TILE_SIZE - 6), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 25))
        for (x, y) in self.room.get_occupied_tiles():
            self.screen.blit(
                overlay,
                (
                    GRID_OFFSET_X + x * self.TILE_SIZE + 3,
                    GRID_OFFSET_Y + y * self.TILE_SIZE + 3,
                ),
            )

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                self.hover_tile = self.get_tile_from_mouse(event.pos)
            
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom in/out with mouse wheel
                if event.y > 0:  # Scroll up = zoom in
                    self.zoom_level = min(self.max_zoom, self.zoom_level + self.zoom_step)
                    print(f"Zoom: {self.zoom_level:.1f}x")
                elif event.y < 0:  # Scroll down = zoom out
                    self.zoom_level = max(self.min_zoom, self.zoom_level - self.zoom_step)
                    print(f"Zoom: {self.zoom_level:.1f}x")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    tile = self.get_tile_from_mouse(event.pos)
                    if self.ladder_mode and tile:
                        if self.ladder_start_point is None:
                            self.ladder_start_point = tile
                        else:
                            # Place ladder segment
                            self.add_ladder_segment(self.ladder_start_point, tile)
                            self.ladder_start_point = None
                    elif not self.ladder_mode:
                        # Try to select a ladder section
                        section, ladder = self.get_section_at_position(event.pos)
                        if section:
                            self.selected_section = section
                            print(f"Selected section {section.section_id} from {ladder.ladder_id} ({int(section.width)}cm wide)")
                        else:
                            self.selected_section = None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_r:
                    # Add rack at hover tile
                    if self.hover_tile and self.placement_mode == "rack":
                        self.add_rack_at_tile(*self.hover_tile)
                
                elif event.key == pygame.K_b:
                    # Add obstacle at hover tile
                    if self.hover_tile and self.placement_mode == "obstacle":
                        self.add_obstacle_at_tile(*self.hover_tile)
                
                elif event.key == pygame.K_t:
                    # Toggle between rack and obstacle placement mode
                    self.placement_mode = "obstacle" if self.placement_mode == "rack" else "rack"
                    print(f"Placement mode: {self.placement_mode.upper()}")
                
                elif event.key == pygame.K_l:
                    # Toggle ladder mode
                    self.ladder_mode = not self.ladder_mode
                    self.ladder_start_point = None
                    self.selected_section = None
                    print(f"Ladder mode: {'ON' if self.ladder_mode else 'OFF'}")
                
                elif event.key == pygame.K_c:
                    # Clear selection and ladder start point
                    self.ladder_start_point = None
                    self.selected_section = None
                    print("Cleared selection")
                
                elif event.key == pygame.K_DELETE:
                    # Delete selected section
                    if self.selected_section:
                        # Find which ladder contains this section
                        for ladder in self.ladders:
                            if self.selected_section in ladder.sections:
                                ladder.sections.remove(self.selected_section)
                                print(f"Deleted section {self.selected_section.section_id}")
                                # If ladder is now empty, remove it
                                if not ladder.sections:
                                    self.ladders.remove(ladder)
                                    print(f"Removed empty ladder {ladder.ladder_id}")
                                self.selected_section = None
                                break

                elif event.key == pygame.K_n:
                    # Finalize current ladder and start a new one on next section
                    self.current_ladder = None
                    self.ladder_start_point = None
                    print("Started a new ladder (next segment creates it)")

                elif event.key == pygame.K_u:
                    # Undo last section
                    target = None
                    if self.current_ladder and self.current_ladder.sections:
                        target = self.current_ladder
                    elif self.ladders:
                        last = self.ladders[-1]
                        if last.sections:
                            target = last
                    if target and target.sections:
                        removed = target.sections.pop()
                        print(f"Undid section {removed.section_id}")
                    else:
                        print("Nothing to undo")

                elif event.key == pygame.K_x:
                    # Delete last ladder
                    if self.ladders:
                        last = self.ladders.pop()
                        if self.current_ladder is last:
                            self.current_ladder = None
                        print(f"Deleted ladder {last.ladder_id}")
                    else:
                        print("No ladders to delete")

                elif event.key == pygame.K_s:
                    # Save layout
                    self.save_layout("layout.json")

                elif event.key == pygame.K_o:
                    # Load layout
                    self.load_layout("layout.json")
                
                elif event.key == pygame.K_h:
                    # Toggle help overlay
                    self.show_help = not self.show_help
                    print(f"Help overlay: {'ON' if self.show_help else 'OFF'}")

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_racks()
            self.draw_obstacles()
            self.draw_ladders()
            
            # Draw ladder preview if in ladder mode
            if self.ladder_mode:
                mouse_pos = pygame.mouse.get_pos()
                self.draw_ladder_preview(mouse_pos)
            
            # Draw help overlay (on top of everything if toggled)
            self.draw_help_overlay()
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()


def main():
    print("Starting Cable Ladder Manager GUI...")
    print("\nControls:")
    print("  Left Click: Place ladder segment (click start, then end)")
    print("  R: Add new rack (2x2) at cursor position")
    print("  L: Toggle ladder placement mode")
    print("  C: Clear current ladder segment")
    print("  ESC: Exit\n")
    
    app = LadderManagerGUI()
    app.run()


if __name__ == "__main__":
    main()
