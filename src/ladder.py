'''
@file: ladder.py
@author: airside-tech

Ladder objects are composed of multiple sections, each with specific attributes.
If the ladder has curved sections, the degree of curvature is also specified, otherwise
it defaults to 0 (straight section).

'''


class Section:
    def __init__(
        self,
        section_id: str,
        x_coord: float,
        y_coord: float,
        length: float,
        orientation: str,
        bend_degree: float = 0.0,
        width: float = 30.0,
        material: str = "aluminum",
    ) -> None:
        # Identity
        self.section_id = section_id

        # Geometry
        self.x_coord = x_coord  # x coordinate start in the layout [m], relative to room origin
        self.y_coord = y_coord  # y coordinate start in the layout [m], relative to room origin
        self.length = length    # length in meters
        self.orientation = orientation  # "horizontal" or "vertical"

        # Physical attributes
        self.width = width              # width in centimeters
        self.material = material
        # degree of curvature, 0 for straight sections, +ve for right bend, -ve for left bend
        self.curved_degree = bend_degree


class Ladder:
    def __init__(self, ladder_id: str) -> None:
        self.ladder_id = ladder_id
        self.sections: list[Section] = []  # List of Section objects

    def add_section(self, section: "Section") -> None:
        self.sections.append(section)

    @property
    def total_length(self) -> float:
        return sum(section.length for section in self.sections)