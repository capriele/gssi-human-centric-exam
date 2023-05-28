from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union


class Room:
    rooms = []

    def __init__(self, name: str, door: Point, polygon: Polygon = None, door_polygon: Polygon = None,  color: str = "#FFFFFF"):
        self.name = name
        self.color = color
        self.door = door
        self.door_polygon = door_polygon
        self.polygon = polygon
        if self.polygon is not None:
            self.center = polygon.centroid
        else:
            self.center = Point(0, 0)

        Room.rooms.append(self)

    @staticmethod
    def min_bounding_rectangle():
        polygons = []
        for r in Room.rooms:
            polygons.append(r.polygon)
        merged_polygon = unary_union(polygons)
        x, y = merged_polygon.envelope.exterior.coords.xy
        x_min = min(x)
        x_max = max(x)
        y_min = min(y)
        y_max = max(y)
        return x_min, x_max, y_min, y_max

    def width(self):
        x, y = self.polygon.minimum_rotated_rectangle.exterior.coords.xy
        edge_length = (Point(x[0], y[0]).distance(Point(x[1], y[1])),
                       Point(x[1], y[1]).distance(Point(x[2], y[2])))
        return min(edge_length)

    def length(self):
        x, y = self.polygon.minimum_rotated_rectangle.exterior.coords.xy
        edge_length = (Point(x[0], y[0]).distance(Point(x[1], y[1])),
                       Point(x[1], y[1]).distance(Point(x[2], y[2])))
        return max(edge_length)

    def __str__(self):
        return self.name + ": [" + str(self.polygon) + "]"
