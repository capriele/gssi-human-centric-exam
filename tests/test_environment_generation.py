import matplotlib.pyplot as plt
from shapely.ops import unary_union
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import numpy as np
from ursina import *
import sys
import os
sys.path.append(os.getcwd())


class Room:
    def __init__(self, name, door_polygon, polygon):
        self.name = name
        self.door = None
        self.door_polygon = None
        if door_polygon is not None:
            self.door = door.centroid
            self.door_polygon = door
        self.center = polygon.centroid
        self.polygon = polygon

    def __str__(self):
        return self.name + ": [" + str(self.polygon) + "]"


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


patients = ["Bob", "Alice"]
roomsCount = len(patients) + 2
roomSize = (150, 200)
doorSize = 65
wallTickness = 1
map = np.zeros((roomSize[0]*roomsCount, 300))
mapSize = map.shape
map[0:wallTickness, :] = 1
map[mapSize[0]-wallTickness:mapSize[0], :] = 1
map[:, 0:wallTickness] = 1
map[:, mapSize[1]-wallTickness:mapSize[1]] = 1

x1 = 0 + wallTickness
y1 = 0 + wallTickness
x2 = mapSize[0] - wallTickness
y2 = mapSize[1] - roomSize[1] - wallTickness
corridor_polygon = Polygon([
    (x1, y1),
    (x1, y2),
    (x2, y2),
    (x2, y1),
])
# plt.plot(*corridor_polygon.exterior.xy)

rooms = [
    Room(
        name="Corridor",
        door_polygon=None,
        polygon=corridor_polygon,
    ),
]

for i in range(0, roomsCount):
    # Vertical
    map[i*roomSize[0]:i*roomSize[0]+wallTickness,
        mapSize[1]-roomSize[1]:mapSize[1]] = 1

    # Horizontal
    map[i*roomSize[0]:(i+1)*roomSize[0]-doorSize, mapSize[1] -
        roomSize[1]:mapSize[1]-roomSize[1]+wallTickness] = 1

    x1 = i*roomSize[0] + wallTickness
    y1 = mapSize[1]-roomSize[1] + wallTickness
    x2 = (i+1)*roomSize[0] - wallTickness
    y2 = mapSize[1] - wallTickness
    room_polygon = Polygon([
        (x1, y1),
        (x1, y2),
        (x2, y2),
        (x2, y1),
    ])
    center = room_polygon.centroid

    x1 = (i+1)*roomSize[0]-doorSize + wallTickness
    y1 = mapSize[1]-roomSize[1] - wallTickness - 10
    x2 = (i+1)*roomSize[0] - wallTickness
    y2 = mapSize[1]-roomSize[1] + wallTickness + 5
    door_polygon = Polygon([
        (x1, y1),
        (x1, y2),
        (x2, y2),
        (x2, y1),
    ])
    door = door_polygon.centroid

    rooms.append(
        Room(
            name="Room " + str(i+1),
            door_polygon=door_polygon,
            polygon=room_polygon,
        )
    )

    route_space_polygon = unary_union(
        [corridor_polygon, door_polygon, room_polygon])
    # plt.plot(*route_space_polygon.exterior.xy)
    '''
    plt.plot(*room_polygon.exterior.xy)
    plt.plot(*door_polygon.exterior.xy)
    plt.plot(door.x, door.y, marker="o", markersize=5,
             markeredgecolor="red", markerfacecolor="red")
    plt.plot(center.x, center.y, marker="o", markersize=5,
             markeredgecolor="green", markerfacecolor="green")
    '''

# plt.matshow(map)
# plt.show()

for r in rooms:
    print(r)


app = Ursina(size=(mapSize[0], mapSize[1]*2))
scale = 0.3
for iy, ix in np.ndindex(map.shape):
    val = map[iy, ix]
    if val == 1:
        Wall(
            scale=(1*scale, 1*scale, 10*scale),
            position=((iy-mapSize[0]/2)*scale, (ix-mapSize[1]/2)*scale, 0)
        )

cp = Vec3(0, 0, mapSize[0]/6)
camera.position = cp
camera.rotation_y = 180
camera.rotation_x = 0
camera.rotation_z = 0

# Sky()
Entity(
    model="plane", color=color.black, scale=200, rotation=(0, -90, 90)
)  # , collider="box"


def input(key):
    global cp
    if key == "escape":
        quit()
    elif key == "space":
        robot.y += 1
        invoke(setattr, robot, "y", robot.y - 1, delay=0.25)
    elif "up arrow" in key:
        camera.rotation_y += 1
    elif "down arrow" in key:
        camera.rotation_y -= 1
    elif "left arrow" in key:
        camera.rotation_x += 1
    elif "right arrow" in key:
        camera.rotation_x -= 1
    elif key == "scroll up":
        cp = Vec3(cp.x, cp.y, cp.z-10)
        camera.position = cp
    elif key == "scroll down":
        cp = Vec3(cp.x, cp.y, cp.z+10)
        camera.position = cp
    elif key == "left mouse up":
        ox = -0.199021 - 0.3375785168685913 + 0.6643332242965698 / 2
        oy = 0.109775 + 0.16665083847045897 - 0.32824939489364624 / 2
        mx = 2 * (mouse.position.x - ox) / (-0.6643332242965698)
        my = 2 * (mouse.position.y - oy) / (0.32824939489364624)
        print(Vec3(30 * mx, 15 * my, 0))


app.run()
