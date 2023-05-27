from roboticstoolbox import *
from roboticstoolbox.mobile import *
import matplotlib.pyplot as plt
import numpy as np
import scipy
from math import pi
import time
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union, cascaded_union

house = scipy.io.loadmat("./data/map.mat")
# map = house["map"]

'''
lattice = LatticePlanner(occgrid=map, root=(10, 10, 0))
lattice.plan()
path, status = lattice.query(start=(10, 10, 0), goal=(45, 211, 0))
lattice.plot(path=path)
plt.show(block=True)
'''
'''
dx = DistanceTransformPlanner(map, metric="euclidean")
time_start = time.time()
dx.start = [44, 170]
dx.goal = [103, 123]
dx.plan()
path = dx.query(start=dx.start, goal=dx.goal)
time_end = time.time()
print(time_end - time_start)
dx.plot(path, block=True)
'''

patients = ["Bob", "Alice", "Test", "TT", "Test",
            "TT", "Test", "TT", "Test", "TT", "Test", "TT"]
patientsCount = len(patients)
roomsCount = (patientsCount+2)
roomSize = (150, 175)
doorSize = 65
map = np.zeros((150*roomsCount, 300))
x, y = map.shape
map[0:5, :] = 1
map[x-5:x, :] = 1
map[:, 0:5] = 1
map[:, y-5:y] = 1

print(map.shape)

corridor = Polygon([
    Point(5, 5),
    Point(5, 125-15),
    Point(x-5, 125-15),
    Point(x-5, 5),
])
living_room = Polygon([
    Point(5, 120),
    Point(5, y-5),
    Point(150-5, y-5),
    Point(150-5, 120),
])
living_room_door = Polygon([
    Point(roomSize[0] - doorSize + 5, y-roomSize[1] - 20),
    Point(roomSize[0] - doorSize + 5, y-roomSize[1] + 5),
    Point(roomSize[0] - 5, y-roomSize[1] + 5),
    Point(roomSize[0] - 5, y-roomSize[1] - 20),
])
fig, axs = plt.subplots()
axs.set_aspect('equal', 'datalim')

colors = [
    "orange",
    "blue",
    "black",
    "red",
    "yellow",
    "green",
]
for i in range(0, roomsCount):
    # horizontal
    map[roomSize[0]*i:roomSize[0]*i+5, y-roomSize[1]:y] = 1

    # vertical
    map[roomSize[0]*i:roomSize[0] *
        (i+1) - doorSize, y-roomSize[1]:y-roomSize[1]+5] = 1

    door_polygon = Polygon([
        Point(roomSize[0] * (i+1) - doorSize + 5, y-roomSize[1] - 15),
        Point(roomSize[0] * (i+1) - doorSize + 5, y-roomSize[1] + 5),
        Point(roomSize[0] * (i+1) - 5, y-roomSize[1] + 5),
        Point(roomSize[0] * (i+1) - 5, y-roomSize[1] - 15),
    ])

    polygon = Polygon([
        Point(roomSize[0]*i+5, y-roomSize[1]-5),
        Point(roomSize[0]*i+5, y-5),
        Point(roomSize[0] * (i+1)-5, y-5),
        Point(roomSize[0] * (i+1)-5, y-roomSize[1]-5),
    ])
    door_center = Point(door_polygon.centroid.x, door_polygon.centroid.y-30)
    center = polygon.centroid
    movement = unary_union(
        [corridor, living_room_door, living_room, door_polygon, polygon])

    if i >= 2:
        if isinstance(movement, Polygon):
            # pass
            plt.plot(*movement.exterior.xy)
        else:
            for geom in movement.geoms:
                xs, ys = geom.exterior.xy
                axs.fill(xs, ys, alpha=0.5, fc=colors[i], ec='none')
    else:
        pass
        # plt.plot(*polygon.exterior.xy)
        # plt.plot(*door_polygon.exterior.xy)

    plt.plot(center.x, center.y, marker="o", markersize=2,
             markeredgecolor="black", markerfacecolor="black")
    plt.plot(door_center.x, door_center.y, marker="o", markersize=2,
             markeredgecolor="green", markerfacecolor="green")

# plt.matshow(map)
# planner = Bug2(occgrid=map)
# planner.plot(block=True)
plt.show()
