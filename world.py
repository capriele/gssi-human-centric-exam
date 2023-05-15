from ursina import *
import matplotlib.pyplot as plt
from roboticstoolbox import *
import numpy as np
from shapely.geometry import Point
import scipy


class World:

    def robotBaseCoords(self):
        return Vec3(-8.66907, -10.6577, 0)

    def medicalRoomCoords(self):
        return Vec3(-8.66907, 10.0107, 0)

    def aliceRoomDoorCoords(self):
        return Vec3(9.51363, -7.97634, 0)

    def bobRoomDoorCoords(self):
        return Vec3(27.6749, -8.15384, 0)

    def findPlayer(self, name):
        for player in self.players:
            if player.name.lower() == name.lower():
                return player
        return None

    def point2map(self, point):
        x = ((point.x + abs(self.x_min))/self.step)-1
        y = ((point.y + abs(self.y_min))/self.step)-1
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        return Point(y, x)

    def point2map2(self, point):
        x = ((point.x + abs(self.x_min))/self.step)-1
        y = ((point.y + abs(self.y_min))/self.step)-1
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        return Point(x, y)

    def map2point(self, point):
        x = point.x*self.step - abs(self.y_min)
        y = point.y*self.step - abs(self.x_min)
        return Point(y, x)

    @staticmethod
    def findPath(world, planner, start, goal, use_next=False):
        path = []
        start = world.point2map(Point(start.x, start.y))
        goal = world.point2map(Point(goal.x, goal.y))
        try:
            if world.use_distance_transform:
                planner.start = [start.x, start.y]
                planner.goal = [goal.x, goal.y]
                # planner.plan()
                if use_next:
                    path_tmp = planner.next(planner.start)
                else:
                    path_tmp = planner.query(
                        start=planner.start, goal=planner.goal)

                if path_tmp:
                    path_tmp = [path_tmp]
                else:
                    return None

                # planner.plot(path_tmp, block=True)
                for point in path_tmp:
                    if hasattr(point, "__len__"):
                        path.append(world.map2point(Point(point[0], point[1])))
            else:
                path_tmp = planner.run(
                    [start.x, start.y], [goal.x, goal.y])
                # path_tmp = planner.query([goal.x, goal.y])
                # planner.plot(path_tmp, block=True)
                for point in path_tmp:
                    if hasattr(point, "__len__"):
                        # path.insert(0, world.map2point(Point(point[0], point[1])))
                        path.append(world.map2point(Point(point[0], point[1])))
        except:
            pass
        return path

    def __init__(self, players, walls, step=0.1, create_map=False, use_distance_transform=False):
        self.players = players
        self.walls = walls
        self.step = step
        self.x_min = -30.0
        self.x_max = 30.0
        self.y_min = -15.0
        self.y_max = 15.0
        self.polygons = []
        self.use_distance_transform = use_distance_transform

        if create_map:
            x_range = np.arange(self.x_min, self.x_max, self.step)
            y_range = np.arange(self.y_min, self.y_max, self.step)
            self.map = np.zeros((len(x_range), len(y_range)))
            self.map = self.map.astype(np.int32)
            for wall in walls:
                poly = wall.polygon()
                self.polygons.append(poly)
                points = list(poly.exterior.coords)
                p = self.point2map2(Point(points[0][0], points[0][1]))
                x_min = p.x
                x_max = p.x
                y_min = p.y
                y_max = p.y
                for p in points:
                    p = self.point2map2(Point(p[0], p[1]))
                    if p.x < x_min:
                        x_min = p.x
                    if p.x > x_max:
                        x_max = p.x
                    if p.y < y_min:
                        y_min = p.y
                    if p.y > y_max:
                        y_max = p.y
                self.map[int(x_min):int(x_max), int(y_min):int(y_max)] = 1

            self.map[0, :] = 1
            self.map[-1, :] = 1
            self.map[:, 0] = 1
            self.map[:, -1] = 1
            scipy.io.savemat('./data/map.mat', {'map': self.map})
        else:
            house = scipy.io.loadmat("./data/map.mat")
            self.map = house["map"]
        self.planner = self.createPlanner()

    def createPlanner(self):
        if self.use_distance_transform:
            p = DistanceTransformPlanner(self.map.copy(), start=[
                                         10, 10], goal=[11, 11])
            p.plan()
            return p
        else:
            return Bug2(occgrid=self.map.copy())
