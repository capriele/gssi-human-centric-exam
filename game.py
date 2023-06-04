from ursina import *
from configurer import Configurer
from constants import Constants
from logger import Logger
from entities import *

import threading
import time

import os
import xmltodict


class Action:
    def __init__(self, name, dict=None):
        self.name = name
        if dict and "exception" in dict:
            if "action" in dict["exception"]:
                _actions = dict["exception"]["action"]
                actions = []
                if isinstance(actions, list):
                    for a in _actions:
                        actions.append(
                            Action(a["@name"], a)
                        )
                else:
                    actions.append(
                        Action(_actions["@name"], _actions)
                    )
            else:
                actions = None
            self.exception = Exception(
                dict["exception"]["@name"], actions)
        else:
            self.exception = None

    def __str__(self):
        e = ""
        if self.exception is not None:
            e = str(self.exception)
        return "\t\tAction: " + self.name+"\n\t" + e


class Exception:
    def __init__(self, name, actions):
        self.name = name
        self.actions = actions

    def __str__(self):
        s = ""
        for a in self.actions:
            if a is not None:
                s += str(a)
        return "\tException: " + self.name+"\n\t" + s


class Rule:
    def __init__(self, name, value, exception):
        self.name = name
        self.value = value
        self.exception = exception

    def __str__(self):
        e = ""
        if self.exception is not None:
            e = str(self.exception)
        return "Rule: " + self.name+" = " + str(self.value) + "\n\t" + e


class PersonConfiguration:
    def __init__(self, dict):
        self.name = dict['person']['name']
        self.description = dict['person']['description']
        self.room = int(dict['person']['room'])
        self.color = dict['person']['color']
        self.authonomy = PersonConfiguration.fillRules(
            dict['person']['ethics'], 'autonomy')
        self.privacy = PersonConfiguration.fillRules(
            dict['person']['ethics'], 'privacy')
        self.dignity = PersonConfiguration.fillRules(
            dict['person']['ethics'], 'dignity')

    def __str__(self):
        s = "[" + self.name + " Configuration]:\r\n"
        s += "- Authonomy:\r\n"
        for e in self.authonomy:
            s += "\t" + str(e) + "\r\n"
        s += "- Privacy:\r\n"
        for e in self.privacy:
            s += "\t" + str(e) + "\r\n"
        s += "- Dignity:\r\n"
        for e in self.dignity:
            s += "\t" + str(e) + "\r\n"
        return s

    @staticmethod
    def fillRules(dict, key):
        _list = []
        try:
            elements = dict[key]['rule']
            if isinstance(elements, list):
                for rule in elements:
                    try:
                        action = Action(
                            rule["exception"]["action"]["@name"], rule["exception"]["action"])
                    except:
                        action = None
                    try:
                        exception = Exception(
                            rule["exception"]["@name"], [action])
                    except:
                        exception = None
                    _list.append(
                        Rule(rule["@name"], rule["@value"], exception)
                    )
            else:
                try:
                    action = Action(
                        elements["exception"]["action"]["@name"], elements["exception"]["action"])
                except:
                    action = None
                try:
                    exception = Exception(
                        elements["exception"]["@name"], [action])
                except:
                    exception = None
                _list.append(
                    Rule(elements["@name"], elements["@value"], exception)
                )
        except:
            pass
        return _list


class WorldCreator:
    def __init__(self, configuration, roomSize=(150, 200), doorSize=65, wallTickness=1, scale=0.1, resolution=1):
        rooms_id = []
        rooms_name = []
        rooms_color = []
        for r in configuration.get_hospital().get_rooms().get_room():
            rooms_id.append(r.get_id())
            rooms_name.append(r.get_name())
            rooms_color.append(r.get_color())

        roomSize = (int(roomSize[0]*resolution), int(roomSize[1]*resolution))
        doorSize = int(doorSize*resolution)

        roomsCount = len(rooms_name)
        self.scale = scale
        self.map = np.zeros(
            (int(roomSize[0]*roomsCount), int(roomSize[1]+100*resolution))
        )
        mapSize = self.map.shape
        self.map[0:wallTickness, :] = 1
        self.map[mapSize[0]-wallTickness:mapSize[0], :] = 1
        self.map[:, 0:wallTickness] = 1
        self.map[:, mapSize[1]-wallTickness:mapSize[1]] = 1

        x1 = 0 + wallTickness
        y1 = 0 + wallTickness
        x2 = mapSize[0] - wallTickness
        y2 = mapSize[1] - roomSize[1] - wallTickness
        x1 = -(x1-self.map.shape[0]/2)*self.scale
        x2 = -(x2-self.map.shape[0]/2)*self.scale
        y1 = (y1-self.map.shape[1]/2)*self.scale
        y2 = (y2-self.map.shape[1]/2)*self.scale
        corridor_polygon = Polygon([
            (x1, y1),
            (x1, y2),
            (x2, y2),
            (x2, y1),
        ])

        self.corridor = Room(
            id=-1,
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

            x1 = (i)*roomSize[0] + wallTickness
            y1 = mapSize[1]-roomSize[1] - wallTickness - 10
            x2 = (i)*roomSize[0] + doorSize - wallTickness
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
                    id=rooms_id[i],
                    name=rooms_name[i],
                    door=door,
                    door_polygon=door_polygon,
                    polygon=room_polygon,
                    color=rooms_color[i]
                )
            )

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
scale = 0.1
wc = WorldCreator(
    configuration=configuration,
    scale=scale,
)
app = Ursina(size=(wc.map.shape[0], wc.map.shape[1]*2))
wc.create_map()
patients = []
directory = 'patients'
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        file = open(f).read()
        data = xmltodict.parse(file)
        patient = PersonConfiguration(data)
        print(patient)
        patients.append(patient)
for patient in patients:
    room = next(
        (room for room in wc.rooms if room.id == patient.room),
        None
    )
    if room is not None:
        p = Player(
            model="cube",
            collider="sphere",
            name=patient.name,
            is_human=True,
            color=color.hex(patient.color),
            position=Vec3(room.center.x, room.center.y, 0),
            scale=2,
        )
        p.setPatientConfiguration(patient)

length = wc.corridor.length()
robot = Player(
    model="cube",
    collider="sphere",
    name=configuration.get_name(),
    is_human=False,
    color=color.hex(configuration.get_color()),
    position=Vec3(wc.corridor.center.x, wc.corridor.center.y, 0),
)

nurse = Player(
    model="cube",
    collider="sphere",
    name="Nurse",
    is_human=True,
    is_staff=True,
    color=color.white,
    position=Vec3(wc.corridor.center.x - length/3.0, wc.corridor.center.y, 0),
    scale=2,
)

world = World(Player.entities, Wall.entities, step=0.1, world_creator=wc)
for p in Player.entities:
    p.setWorld(world)
robotClass = Robot(robot, world, configuration)

status_text = Text("", color=color.green, scale=1, x=-0.6, y=-0.36, z=0)
conversation_text = Text("", color=color.red, scale=1, x=-0.6, y=-0.4, z=0)

cp = Vec3(0, 0, 110)
camera.position = cp
camera.rotation_y = 180
camera.rotation_x = 0
camera.rotation_z = 0
# camera.look_at(robot)


def input(key):
    global cp
    if key == "escape":
        quit()
    elif "scroll up" in key:
        cp.z += 2
        camera.position = cp
    elif "scroll down" in key:
        cp.z -= 2
        camera.position = cp


pressed_key = None


def unset_pressed_key(seconds):
    global pressed_key
    time.sleep(seconds)
    Logger.i("Keys re-enabled...")
    pressed_key = None


def disable_held_keys(key):
    global pressed_key
    pressed_key = key
    held_keys[key] = 0
    Logger.i(
        f"Disabling keys for {Constants.TIMEOUT_IN_SECONDS_TO_REACTIVATE_KEYS} seconds...")
    lock = threading.Lock()
    lock.acquire()
    thread = threading.Thread(target=unset_pressed_key, args=[
                              Constants.TIMEOUT_IN_SECONDS_TO_REACTIVATE_KEYS])
    thread.start()
    lock.release()


def update():
    global pressed_key

    if held_keys[Constants.KEY_RESET] == 1:
        Logger.i(f"Pressed key {held_keys[Constants.KEY_RESET]}...")
        disable_held_keys(Constants.KEY_RESET)
        robotClass.reset()
    if held_keys[Constants.KEY_START] == 1:
        Logger.i(f"Pressed key {held_keys[Constants.KEY_START]}...")
        disable_held_keys(Constants.KEY_START)
        robotClass.startDailyActivities()
    if robotClass.isWaitingAnswer():
        if held_keys[Constants.KEY_YES] == 1:
            Logger.i(f"Pressed key {held_keys[Constants.KEY_YES]}...")
            disable_held_keys(Constants.KEY_YES)
            robotClass.setAnswer(True)
        elif held_keys[Constants.KEY_NO] == 1:
            Logger.i(f"Pressed key {held_keys[Constants.KEY_NO]}...")
            disable_held_keys(Constants.KEY_NO)
            robotClass.setAnswer(False)

    Room.write_rooms_name()

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


Entity(
    model="plane", color=color.black, scale=200, rotation=(0, -90, 90)
)

window.title = Constants.WINDOW_TITLE
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = False

# start running the game
app.run()
