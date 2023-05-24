from ursina import *
from ursina.prefabs.conversation import Conversation
from ursina.prefabs.first_person_controller import FirstPersonController
from enum import Enum
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from robot import Robot
import random
from world import World
from roboticstoolbox import DistanceTransformPlanner

import threading
import time

app = Ursina(size=(600, 600))


class Player(Entity):
    entities = []

    def load_profile(self):
        print("Load " + str(self.name) + " profile")
        return []

    def __init__(self, name="Player", is_human=False, is_staff=False, add_to_scene_entities=True, **kwargs):
        super().__init__(add_to_scene_entities=add_to_scene_entities, **kwargs)
        self.name = name
        self.is_human = is_human
        self.is_staff = is_staff
        self.base_color = self.color
        self.collider = BoxCollider(
            self, center=Vec3(0, 0, 0), size=Vec3(2, 2, 2))
        self.path = []
        self.goal = None
        self.room = None
        self.world = None
        self.planner = None
        self.initialPosition = self.position
        self.area = None
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.update_thread, args=())
        Player.entities.append(self)
        # TODO: uncomment to make the player moving
        # self.thread.start()
        # self.collider.visible = True

    def update_thread(self):
        while True:
            if self.is_human and self.world is not None and self.area is not None and not self.path:
                self.goal = self.world.randomPointsInPolygon(
                    self.area, Point(self.position.x, self.position.y))
                if self.goal is not None:
                    tmp_path = World.findPath(
                        self.world, self.planner, self.position, self.goal)
                    self.lock.acquire()
                    self.path.extend(tmp_path)
                    self.lock.release()
            time.sleep(1.5)

    def setWorld(self, world):
        self.world = world
        self.planner = self.world.createUserPlanner(self)
        self.room = next(
            (x for x in self.world.rooms if self.name.lower() in x.name.lower()), None)
        if self.name == "Alice":
            self.area = self.world.aliceMovementPolygon()
        elif self.name == "Bob":
            self.area = self.world.bobMovementPolygon()
        else:
            self.room = self.initialPosition

    def update(self):
        if self.is_human:
            self.lock.acquire()
            if self.path:
                p = self.path.pop(0)
                # origin = self.world_position
                # ignore = [self.model]
                # ignore.extend(self.world.players)
                # hit_info = raycast(origin, Vec3(p.x, p.y, 0),
                #                   ignore=ignore, distance=1, debug=False)
                # if not hit_info.hit:
                self.position = Vec3(p.x, p.y, 0)
                # else:
                #    self.path = []
            else:
                self.goal = None
            self.lock.release()


class Wall(Entity):

    entities = []

    def __init__(self, add_to_scene_entities=True, **kwargs):
        super().__init__(add_to_scene_entities=add_to_scene_entities, **kwargs)
        self.origin_x = 0
        self.origin_y = 0
        self.color = color.gray
        self.model = 'cube'
        self.collider = 'box'
        Wall.entities.append(self)
        self.collider.visible = True

    def polygon(self):
        start, end = self.getTightBounds()
        x1 = start[0]
        y1 = start[1]
        x2 = end[0]
        y2 = end[1]
        return Polygon([
            (x1, y1),
            (x1, y2),
            (x2, y1),
            (x2, y2),
        ])

    def clear(self):
        self.color = color.gray

    def highlight(self):
        self.color = color.yellow


scale = 0.3
'''
bob = Player(model='models/Man.obj', collider='box',
             scale=0.0065, position=Vec3(5, 5, 0))
alice = Player(model='models/Woman.obj', collider='box',
               scale=0.0065, position=Vec3(50, 5, 0))
'''
bob = Player(model='cube', collider='sphere', name="Bob", is_human=True,
             color=color.azure, position=Vec3(23, 10, 0), scale=3)
alice = Player(model='cube', collider='sphere', name="Alice", is_human=True,
               color=color.pink, position=Vec3(6, 10, 0), scale=3)
robot = Player(model='cube', collider='sphere', name="Robot", is_human=False,
               color=color.orange, position=Vec3(-8.66907, -10.6577, 0))
nurse = Player(model='cube', collider='sphere', name="Nurse", is_human=True, is_staff=True,
               color=color.white, position=Vec3(-23, -10, 0), scale=3)


Wall(scale_x=100*scale, scale_y=1, scale_z=1, x=-50*scale, y=-50*scale, z=0)
Wall(scale_x=100*scale, scale_y=1, scale_z=1, x=50*scale, y=-50*scale, z=0)
Wall(scale_x=1, scale_y=50*scale, scale_z=1, x=100*scale, y=25*scale, z=0)
Wall(scale_x=1, scale_y=50*scale, scale_z=1, x=100*scale, y=-25*scale, z=0)
Wall(scale_x=100*scale, scale_y=1, scale_z=1, x=-50*scale, y=50*scale, z=0)
Wall(scale_x=100*scale, scale_y=1, scale_z=1, x=50*scale, y=50*scale, z=0)
Wall(scale_x=1, scale_y=50*scale, scale_z=1, x=-100*scale, y=25*scale, z=0)
Wall(scale_x=1, scale_y=50*scale, scale_z=1, x=-100*scale, y=-25*scale, z=0)
Wall(scale_x=1, scale_y=70*scale, scale_z=1, x=-50*scale, y=15*scale, z=0)
Wall(scale_x=1, scale_y=70*scale, scale_z=1, x=0*scale, y=15*scale, z=0)
Wall(scale_x=1, scale_y=70*scale, scale_z=1, x=50*scale, y=15*scale, z=0)
Wall(scale=(45*scale, 1, 1), position=(60*scale, -20*scale, 0))
Wall(scale=(45*scale, 1, 1), position=(0*scale, -20*scale, 0))
Wall(scale=(45*scale, 1, 1), position=(-60*scale, -20*scale, 0))
world = World(Player.entities, Wall.entities, step=0.1, create_map=True)
bob.setWorld(world)
alice.setWorld(world)
nurse.setWorld(world)

Text(
    "Living Room", color=color.green, position=(0.46, 0.38, 0), scale=.7)

Text(
    "Medical Room", color=color.white, position=(0.09, 0.38, 0), scale=.7)

Text(
    "Alice Room", color=color.pink, position=(-0.2, 0.38, 0), scale=.7)

Text(
    "Bob Room", color=color.azure, position=(-0.6, 0.38, 0), scale=.7)
status_text = Text("", color=color.green, scale=1,
                   x=-0.6, y=-0.36, z=0)
conversation_text = Text("", color=color.red, scale=1,
                         x=-0.6, y=-0.4, z=0)

robotClass = Robot(robot, world)
'''
camera.position = (-40, -230, 200)
camera.rotation_y = 170
camera.rotation_x = -50
camera.rotation_z = 0
'''
cp = Vec3(0, 0, 100)
camera.position = cp
camera.rotation_y = 180
camera.rotation_x = 0
camera.rotation_z = 0
# camera.look_at(robot)

# this part will make the player move left or right based on our input.
# to check which keys are held down, we can check the held_keys dictionary.
# 0 means not pressed and 1 means pressed.
# time.dt is simply the time since the last frame. by multiplying with this, the
# player will move at the same speed regardless of how fast the game runs.


def input(key):
    if key == 'escape':
        quit()
    elif key == 'space':
        robot.y += 1
        invoke(setattr, robot, 'y', robot.y-1, delay=.25)
    elif key == 'left mouse up':
        ox = -0.199021 - 0.3375785168685913 + 0.6643332242965698/2
        oy = 0.109775 + 0.16665083847045897 - 0.32824939489364624/2
        mx = 2*(mouse.position.x - ox) / (-0.6643332242965698)
        my = 2*(mouse.position.y - oy) / (0.32824939489364624)
        print(Vec3(30*mx, 15*my, 0))
    '''
    elif key == 'scroll up':
        cp[0] += 0
        cp[1] += 0
        cp[2] += 0
        camera.position = cp
        camera.rotation_x += 1
        camera.rotation_y += 1
        camera.rotation_z += 0
    elif key == 'scroll down':
        cp[0] -= 0
        cp[1] -= 0
        cp[2] -= 0
        camera.position = cp
        camera.rotation_x -= 1
        camera.rotation_y -= 1
        camera.rotation_z -= 0
    '''


def update():

    if held_keys["r"]:
        robotClass.reset()
    if held_keys["s"]:
        robotClass.startDailyActivities()
    if robotClass.isWaitingAnswer():
        if held_keys["y"]:
            robotClass.setAnswer(True)
        elif held_keys["n"]:
            robotClass.setAnswer(False)
    robotClass.update(dt=time.dt, status_text=status_text,
                      conversation_text=conversation_text)

    for p in Player.entities:
        p.update()
        if p != robot:
            if robot.intersects(p).hit:
                p.color = color.lime
                robotClass.interactWith(p)
            else:
                p.color = p.base_color


# Sky()
Entity(model="plane", color=color.black, scale=200,
       rotation=(0, -90, 90))  # , collider="box"

window.title = "Human-Centric Simulation"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = True
window.fps_counter.enabled = True

# start running the game
app.run()
