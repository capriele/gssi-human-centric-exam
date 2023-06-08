from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union
from ursina import *


class Room:
    rooms = []
    rooms_name_entities = []

    def __init__(self, id: int, name: str, door: Point, polygon: Polygon = None, door_polygon: Polygon = None,  color: str = "#FFFFFF"):
        self.id = id
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

    @staticmethod
    def write_rooms_name():
        x_min, x_max, y_min, y_max = Room.min_bounding_rectangle()
        for t in Room.rooms_name_entities:
            destroy(t)
        for room in Room.rooms:
            if room.name.lower() != "corridor":
                point = world_position_to_screen_position(
                    (room.center.x, room.center.y))
                point2 = world_position_to_screen_position(
                    (room.center.x, y_max + 1))
                t = Text(
                    room.name,
                    color=color.hex(room.color),
                    origin=(0, 0, 0),
                    position=(point.x, point2.y, 0),
                    scale=0.7
                )
                Room.rooms_name_entities.append(t)

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
