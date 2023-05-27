from ursina import *
from configurer import Configurer
from constants import Constants
from logger import Logger
from entities import *

import threading
import time

app = Ursina(size=(600, 600))

scale = 0.3

configuration = Configurer().load_base_configuration()
for r in configuration.get_hospital().get_rooms().get_room():
    patient = r.get_patients().get_patient()
    Player(
        model="cube",
        collider="sphere",
        name=patient.get_name(),
        is_human=True,
        color=color.hex(patient.get_color()),
        position=Vec3(patient.get_position_x(), patient.get_position_y(), 0),
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


Wall(scale_x=100 * scale, scale_y=1, scale_z=1,
     x=-50 * scale, y=-50 * scale, z=0)
Wall(scale_x=100 * scale, scale_y=1, scale_z=1, x=50 * scale, y=-50 * scale, z=0)
Wall(scale_x=1, scale_y=50 * scale, scale_z=1, x=100 * scale, y=25 * scale, z=0)
Wall(scale_x=1, scale_y=50 * scale, scale_z=1,
     x=100 * scale, y=-25 * scale, z=0)
Wall(scale_x=100 * scale, scale_y=1, scale_z=1, x=-50 * scale, y=50 * scale, z=0)
Wall(scale_x=100 * scale, scale_y=1, scale_z=1, x=50 * scale, y=50 * scale, z=0)
Wall(scale_x=1, scale_y=50 * scale, scale_z=1,
     x=-100 * scale, y=25 * scale, z=0)
Wall(scale_x=1, scale_y=50 * scale, scale_z=1,
     x=-100 * scale, y=-25 * scale, z=0)
Wall(scale_x=1, scale_y=70 * scale, scale_z=1, x=-50 * scale, y=15 * scale, z=0)
Wall(scale_x=1, scale_y=70 * scale, scale_z=1, x=0 * scale, y=15 * scale, z=0)
Wall(scale_x=1, scale_y=70 * scale, scale_z=1, x=50 * scale, y=15 * scale, z=0)
Wall(scale=(45 * scale, 1, 1), position=(60 * scale, -20 * scale, 0))
Wall(scale=(45 * scale, 1, 1), position=(0 * scale, -20 * scale, 0))
Wall(scale=(45 * scale, 1, 1), position=(-60 * scale, -20 * scale, 0))
world = World(Player.entities, Wall.entities, step=0.1, create_map=True)
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
