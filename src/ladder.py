'''
@file: ladder.py
@author: airside-tech

Ladder objects are composed of multiple sections, each with specific attributes.
If the ladder has curved sections, the degree of curvature is also specified, otherwise
it defaults to 0 (straight section).

'''


class Section:
    def __init__(self, section_id: str, length: float, orientation: str, curved_degree: float = 0.0, 
                 width: float = 30.0, material: str = "aluminum"):
        self.section_id = section_id
        self.length = length          # length in meters
        self.orientation = orientation # "horizontal" or "vertical"
        self.width = width            # width in centimeters
        self.material = material
        self.curved_degree = curved_degree  # degree of curvature, 0 for straight sections


class Ladder:
    def __init__(self, ladder_id: str):
        self.ladder_id = ladder_id
        self.sections = []  # List of Section objects
    
    def add_section(self, section: Section) -> None:
        self.sections.append(section)
    
    @property
    def total_length(self) -> float:
        return sum(section.length for section in self.sections)