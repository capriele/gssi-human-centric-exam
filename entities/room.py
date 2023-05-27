from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Room:
    def __init__(self, name: str, door: Point, polygon: Polygon = None, door_polygon: Polygon = None):
        self.name = name
        self.door = door
        self.door_polygon = door_polygon
        self.polygon = polygon
        if self.polygon is not None:
            self.center = polygon.centroid
        else:
            self.center = Point(0, 0)

    def __str__(self):
        return self.name + ": [" + str(self.polygon) + "]"
