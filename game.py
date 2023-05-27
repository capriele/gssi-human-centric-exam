from ursina import *
from configurer import Configurer
from constants import Constants
from logger import Logger
from entities import *

import threading
import time
import matplotlib.pyplot as plt


class WorldCreator:
    def __init__(self, configuration, roomSize=(150, 200), doorSize=65, wallTickness=1, scale=0.1):
        rooms_name = []
        for r in configuration.get_hospital().get_rooms().get_room():
            rooms_name.append(r.get_name())

        roomsCount = len(rooms_name)
        self.scale = scale
        self.map = np.zeros((roomSize[0]*roomsCount, roomSize[1]+100))
        mapSize = self.map.shape
        self.map[0:wallTickness, :] = 1
        self.map[mapSize[0]-wallTickness:mapSize[0], :] = 1
        self.map[:, 0:wallTickness] = 1
        self.map[:, mapSize[1]-wallTickness:mapSize[1]] = 1

        x1 = 0 + wallTickness
        y1 = 0 + wallTickness
        x2 = mapSize[0] - wallTickness
        y2 = mapSize[1] - roomSize[1] - wallTickness
        x1 = (x1-self.map.shape[0]/2)*self.scale
        x2 = (x2-self.map.shape[0]/2)*self.scale
        y1 = (y1-self.map.shape[1]/2)*self.scale
        y2 = (y2-self.map.shape[1]/2)*self.scale
        corridor_polygon = Polygon([
            (x1, y1),
            (x1, y2),
            (x2, y2),
            (x2, y1),
        ])

        corridor = Room(
            name="Corridor",
            door=Point(0, 0),
            door_polygon=None,
            polygon=corridor_polygon,
        )

        self.rooms = []

        for i in range(0, roomsCount):
            # Vertical
            self.map[i*roomSize[0]:i*roomSize[0]+wallTickness,
                     mapSize[1]-roomSize[1]:mapSize[1]] = 1

            # Horizontal
            self.map[i*roomSize[0]:(i+1)*roomSize[0]-doorSize, mapSize[1] -
                     roomSize[1]:mapSize[1]-roomSize[1]+wallTickness] = 1

            x1 = i*roomSize[0] + wallTickness
            y1 = mapSize[1]-roomSize[1] + wallTickness
            x2 = (i+1)*roomSize[0] - wallTickness
            y2 = mapSize[1] - wallTickness
            x1 = -(x1-self.map.shape[0]/2)*self.scale
            x2 = -(x2-self.map.shape[0]/2)*self.scale
            y1 = (y1-self.map.shape[1]/2)*self.scale
            y2 = (y2-self.map.shape[1]/2)*self.scale
            room_polygon = Polygon([
                (x1, y1),
                (x1, y2),
                (x2, y2),
                (x2, y1),
            ])

            x1 = (i)*roomSize[0]-doorSize + wallTickness
            y1 = mapSize[1]-roomSize[1] - wallTickness - 10
            x2 = (i+1)*roomSize[0] - wallTickness
            y2 = mapSize[1]-roomSize[1] + wallTickness + 5
            x1 = -(x1-self.map.shape[0]/2)*self.scale
            x2 = -(x2-self.map.shape[0]/2)*self.scale
            y1 = (y1-self.map.shape[1]/2)*self.scale
            y2 = (y2-self.map.shape[1]/2)*self.scale
            door_polygon = Polygon([
                (x1, y1),
                (x1, y2),
                (x2, y2),
                (x2, y1),
            ])
            door = door_polygon.centroid

            self.rooms.append(
                Room(
                    name=rooms_name[i],
                    door=door,
                    door_polygon=door_polygon,
                    polygon=room_polygon,
                )
            )
            colors = [
                color.blue, color.red, color.yellow, color.green
            ]
            '''
            Player(
                model="cube",
                collider="sphere",
                name="test",
                is_human=False,
                color=colors[i],
                position=Vec3(room_polygon.centroid.x,
                              room_polygon.centroid.y, 0),
                scale=2,
            )
            Player(
                model="cube",
                collider="sphere",
                name="test",
                is_human=False,
                color=colors[i],
                position=Vec3(door.x, door.y, 0),
                scale=2,
            )
            plt.plot(*room_polygon.exterior.xy)
            plt.plot(*door_polygon.exterior.xy)
            plt.plot(door.x, door.y, marker="o", markersize=5,
                     markeredgecolor="red", markerfacecolor="red")
            plt.plot(room_polygon.centroid.x, room_polygon.centroid.y, marker="o", markersize=5,
                     markeredgecolor="green", markerfacecolor="green")
            '''

        # plt.show()
        # self.room.insert(len(self.room)-1)

        # route_space_polygon = unary_union(
        #    [corridor_polygon, door_polygon, room_polygon])

    def create_map(self):
        for iy, ix in np.ndindex(self.map.shape):
            val = self.map[iy, ix]
            if val == 1:
                Wall(
                    scale=(1*self.scale, 1*self.scale, 10*self.scale),
                    position=((iy-self.map.shape[0]/2)*self.scale,
                              (ix-self.map.shape[1]/2)*self.scale, 0)
                )

    def __str__(self) -> str:
        s = ""
        for r in self.rooms:
            s += str(r) + "\r\n"
        return s


configuration = Configurer().load_base_configuration()
patients = []
for r in configuration.get_hospital().get_rooms().get_room():
    p = r.get_patients().get_patient()
    if p.get_name().lower() != "fake":
        patients.append(p)

scale = 0.1
wc = WorldCreator(
    configuration=configuration,
    scale=scale,
)
app = Ursina(size=(wc.map.shape[0], wc.map.shape[1]*2))
wc.create_map()
for index, patient in enumerate(patients):
    room = wc.rooms[index]
    Player(
        model="cube",
        collider="sphere",
        name=patient.get_name(),
        is_human=True,
        color=color.hex(patient.get_color()),
        position=Vec3(room.center.x, room.center.y, 0),
        scale=2,
    )

robot = Player(
    model="cube",
    collider="sphere",
    name=configuration.get_name(),
    is_human=False,
    color=color.hex(configuration.get_color()),
    position=Vec3(-8.66907, -10.6577, 0),
)

nurse = Player(
    model="cube",
    collider="sphere",
    name="Nurse",
    is_human=True,
    is_staff=True,
    color=color.white,
    position=Vec3(-23, -10, 0),
    scale=2,
)

world = World(Player.entities, Wall.entities, step=0.1, world_creator=wc)
for p in Player.entities:
    p.setWorld(world)
robotClass = Robot(robot, world, configuration)

Text("Living Room", color=color.green, position=(0.46, 0.38, 0), scale=0.7)
Text("Medical Room", color=color.white, position=(0.09, 0.38, 0), scale=0.7)
Text("Alice Room", color=color.pink, position=(-0.2, 0.38, 0), scale=0.7)
Text("Bob Room", color=color.azure, position=(-0.6, 0.38, 0), scale=0.7)
status_text = Text("", color=color.green, scale=1, x=-0.6, y=-0.36, z=0)
conversation_text = Text("", color=color.red, scale=1, x=-0.6, y=-0.4, z=0)

cp = Vec3(0, 0, 100)
camera.position = cp
camera.rotation_y = 180
camera.rotation_x = 0
camera.rotation_z = 0
# camera.look_at(robot)


def input(key):
    if key == "escape":
        quit()


pressed_key = None


def unset_pressed_key(seconds):
    global pressed_key
    time.sleep(seconds)
    Logger.i("Keys re-enabled...")
    pressed_key = None


def disable_held_keys(key):
    global pressed_key
    Logger.i(
        f"Disabling keys for {Constants.TIMEOUT_IN_SECONDS_TO_REACTIVATE_KEYS} seconds...")
    lock = threading.Lock()
    lock.acquire()
    pressed_key = key
    thread = threading.Thread(target=unset_pressed_key, args=[
                              Constants.TIMEOUT_IN_SECONDS_TO_REACTIVATE_KEYS])
    thread.start()
    lock.release()


def update():
    global pressed_key

    if pressed_key == None:

        if held_keys[Constants.KEY_RESET]:
            Logger.i(f"Pressed key {held_keys[Constants.KEY_RESET]}...")
            disable_held_keys(Constants.KEY_RESET)
            robotClass.reset()
        if held_keys[Constants.KEY_START]:
            Logger.i(f"Pressed key {held_keys[Constants.KEY_START]}...")
            disable_held_keys(Constants.KEY_START)
            robotClass.startDailyActivities()
        if robotClass.isWaitingAnswer():
            if held_keys[Constants.KEY_YES]:
                Logger.i(f"Pressed key {held_keys[Constants.KEY_YES]}...")
                disable_held_keys(Constants.KEY_YES)
                robotClass.setAnswer(True)
            elif held_keys[Constants.KEY_NO]:
                Logger.i(f"Pressed key {held_keys[Constants.KEY_NO]}...")
                disable_held_keys(Constants.KEY_NO)
                robotClass.setAnswer(False)

    robotClass.update(
        dt=time.dt, status_text=status_text, conversation_text=conversation_text
    )

    for p in Player.entities:
        p.update()
        if p != robot:
            if robot.intersects(p).hit:
                p.color = color.lime
                robotClass.interactWith(p)
            else:
                p.color = p.base_color


# Sky()
Entity(
    model="plane", color=color.black, scale=200, rotation=(0, -90, 90)
)  # , collider="box"

window.title = Constants.WINDOW_TITLE
window.borderless = False
window.fullscreen = False
window.exit_button.visible = True
window.fps_counter.enabled = True

# start running the game
app.run()
