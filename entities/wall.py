from ursina import *
from shapely.geometry.polygon import Polygon


class Wall(Entity):
    entities = []

    def __init__(self, add_to_scene_entities=True, **kwargs):
        super().__init__(add_to_scene_entities=add_to_scene_entities, **kwargs)
        self.origin_x = 0
        self.origin_y = 0
        self.color = color.gray
        self.model = "cube"
        self.collider = "box"
        Wall.entities.append(self)
        self.collider.visible = True

    def polygon(self):
        start, end = self.getTightBounds()
        x1 = start[0]
        y1 = start[1]
        x2 = end[0]
        y2 = end[1]
        return Polygon(
            [
                (x1, y1),
                (x1, y2),
                (x2, y1),
                (x2, y2),
            ]
        )

    def clear(self):
        self.color = color.gray

    def highlight(self):
        self.color = color.yellow
