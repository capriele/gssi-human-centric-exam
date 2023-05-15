from ursina import *
from enum import Enum
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Activity(Enum):
    NONE = 0
    MOVING = 1
    GO_TO_MEDICAL_ROOM = 2
    GO_TO_BOB = 3
    GO_TO_ALICE = 4
    WAIT_ALICE_ANSWER = 5
    ALICE_GIVE_PILL = 6
    CALL_NURSE_ALICE = 7
    WAIT_BOB_ANSWER = 8
    BOB_GIVE_PILL = 9
    CALL_NURSE_BOB = 10
    PILL_GIVEN = 11


class Robot:

    def __init__(self, model, world):
        self.model = model
        self.world = world
        self.planner = self.world.createPlanner()
        self.reset()

    def reset(self):
        self.model.position = self.world.robotBaseCoords()
        self.activity = Activity.NONE
        self._delta = 0.05
        self.step = 0
        self.status = ""
        self.conversation = ""
        self.answer = False
        self.pills = 0
        self.path = []
        self.goal = None
        self.onComplete = None

    def setStatus(self, text):
        self.status = text

    def setActivity(self, activity):
        self.activity = activity

    def setPills(self, num):
        self.pills = num

    def setStatus(self, text):
        self.status = text

    def setConversation(self, text):
        self.conversation = text

    def setGoal(self, goal, onComplete=None):
        self.goal = goal
        self.activity = Activity.MOVING
        self.onComplete = onComplete

    def startDailyActivities(self):
        self.setGoal(self.world.medicalRoomCoords(), lambda: (
            self.setPills(2),
            self.setGoal(self.world.robotBaseCoords(), lambda: (
                self.setStatus("Pills taken!"),
                self.setStatus("Pills taken!, Going to Alice's room!"),
                self.setGoal(self.world.aliceRoomDoorCoords(), lambda: (
                    self.setConversation("Alice, can I enter?"),
                    self.setActivity(Activity.WAIT_ALICE_ANSWER),
                )),
            )),
        ))

    def update(self, dt=0, status_text=None, conversation_text=None):
        status_text.text = self.status
        conversation_text.text = self.conversation
        if self.goal is not None:
            self.path = self.world.findPath(
                self.world, self.planner, self.model.position, self.goal)
            self.goal = None
        if self.path:
            p = self.path.pop(0)
            for i in range(0, 1):
                if self.path:
                    self.path.pop(0)
            origin = self.model.world_position
            ignore = [self.model]
            ignore.extend(self.world.players)
            hit_info = raycast(origin, Vec3(p.x, p.y, 0),
                               ignore=ignore, distance=1, debug=False)
            if not hit_info.hit:
                self.model.position = (p.x, p.y, 0)
        else:
            self.activity = Activity.NONE

        if self.activity in [Activity.NONE, Activity.PILL_GIVEN]:
            # call on complete
            if self.onComplete is not None:
                self.onComplete()

    def isWaitingAnswer(self):
        return (self.activity == Activity.WAIT_ALICE_ANSWER or self.activity == Activity.WAIT_BOB_ANSWER)

    def setAnswer(self, answer):
        self.answer = answer
        if self.answer:
            if self.activity == Activity.WAIT_ALICE_ANSWER:
                self.conversation += ", Yes"
                self.status = "Pills taken!, Entering into Alice's room"
                self.activity = Activity.ALICE_GIVE_PILL
                self.setGoal(self.world.findPlayer("alice").position, lambda: (
                    self.setStatus("Going to Bob's room!"),
                    self.setConversation(""),
                    self.setGoal(self.world.aliceRoomDoorCoords(), lambda: (
                        self.setGoal(self.world.bobRoomDoorCoords(), lambda: (
                            self.setConversation("Bob, can I enter?"),
                            self.setActivity(Activity.WAIT_BOB_ANSWER),
                        ))
                    ))
                ))
            elif self.activity == Activity.WAIT_BOB_ANSWER:
                self.conversation += ", Yes"
                self.status = "Pills taken!, Entering into Bob's room"
                self.activity = Activity.BOB_GIVE_PILL
                self.setGoal(self.world.findPlayer("bob").position, lambda: (
                    self.setStatus("Going to Base!"),
                    self.setConversation(""),
                    self.setGoal(self.world.bobRoomDoorCoords(), lambda: (
                        self.setGoal(self.world.robotBaseCoords(), lambda: (
                            self.setConversation(""),
                            self.setStatus(
                                "Base reached. I'll start another activity tomorrow"),
                            self.setActivity(Activity.NONE),
                        ))
                    ))
                ))
        else:
            if self.activity == Activity.WAIT_ALICE_ANSWER:
                self.conversation += ", No"
                self.setStatus("Call nurse for Alice!")
                self.setGoal(self.world.findPlayer("nurse").position, lambda: (
                    self.setConversation(""),
                    self.setGoal(self.world.robotBaseCoords(), lambda: (
                        self.setStatus("Going to Bob's room!"),
                        self.setConversation(""),
                        self.setGoal(self.world.aliceRoomDoorCoords(), lambda: (
                            self.setGoal(self.world.bobRoomDoorCoords(), lambda: (
                                self.setConversation("Bob, can I enter?"),
                                self.setActivity(Activity.WAIT_BOB_ANSWER),
                            ))
                        ))
                    ))
                ))
            elif self.activity == Activity.WAIT_BOB_ANSWER:
                self.conversation += ", No"
                self.setStatus("Call nurse for Bob!")
                self.setGoal(self.world.findPlayer("nurse").position, lambda: (
                    self.setConversation(""),
                    self.setGoal(self.world.robotBaseCoords(), lambda: (
                        self.setStatus(
                             "Base reached. I'll start another activity tomorrow"),
                        self.setActivity(Activity.NONE),
                    ))
                ))

    def interactWith(self, model):
        if model.name.lower() == "alice":
            if self.activity == Activity.ALICE_GIVE_PILL:
                self.activity = Activity.PILL_GIVEN
                self.pills -= 1
                self.status = "Pills taken!, Pill delivered to Alice"
            else:
                self.conversation = "Hi Alice!"
        elif model.name.lower() == "bob":
            if self.activity == Activity.BOB_GIVE_PILL:
                self.activity = Activity.PILL_GIVEN
                self.pills -= 1
                self.status = "Pills taken!, Pill delivered to Bob"
            else:
                self.conversation = "Hi Bob!"
        else:
            self.conversation = "Hi " + model.name + "!"
