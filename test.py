from roboticstoolbox import *
from roboticstoolbox.mobile import *
import matplotlib.pyplot as plt
import numpy as np
import scipy
from math import pi
import time

house = scipy.io.loadmat("./data/map.mat")
map = house["map"]

'''
lattice = LatticePlanner(occgrid=map, root=(10, 10, 0))
lattice.plan()
path, status = lattice.query(start=(10, 10, 0), goal=(45, 211, 0))
lattice.plot(path=path)
plt.show(block=True)
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
