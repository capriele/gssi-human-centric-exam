from ursina import *
from shapely.geometry import Point
from .world import World

import threading
import time


class Player(Entity):
    entities = []

    def __init__(
        self,
        name="Player",
        is_human=False,
        is_staff=False,
        add_to_scene_entities=True,
        **kwargs
    ):
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
        self.patientConfiguration = None
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
            if (
                self.is_human
                and self.world is not None
                and self.area is not None
                and not self.path
            ):
                self.goal = self.world.randomPointsInPolygon(
                    self.area, Point(self.position.x, self.position.y)
                )
                if self.goal is not None:
                    tmp_path = World.findPath(
                        self.world, self.planner, self.position, self.goal
                    )
                    self.lock.acquire()
                    self.path.extend(tmp_path)
                    self.lock.release()
            time.sleep(1.5)

    def setPatientConfiguration(self, configuration):
        self.patientConfiguration = configuration

    def setWorld(self, world):
        self.world = world
        self.planner = self.world.createUserPlanner(self)
        self.room = next(
            (x for x in self.world.rooms if self.name.lower() in x.name.lower()), None
        )

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
