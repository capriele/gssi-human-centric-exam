from ursina import *
from enum import Enum
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from configurer import Configurer
from constants import Constants
from logger import Logger


class Activity(Enum):
    NONE = 0
    MOVING = 1
    GO_TO_MEDICAL_ROOM = 2
    GO_TO_PATIENT = 3
    WAIT_ANSWER = 5
    PATIENT_GIVE_PILL = 6
    CALL_NURSE_FOR_PATIENT = 7
    TAKE_PILLS = 8
    PILL_GIVEN = 9


class PlanStep:

    @staticmethod
    def none():
        return PlanStep(None)

    def __init__(self, target=Point(0, 0), activity=Activity.NONE, status=None, onComplete=None, patient=None):
        self.target = target
        self.activity = activity
        self.status = status
        self.onComplete = onComplete
        self._isTargetReached = False
        self._answer = None
        self._patient = patient

    def targetReached(self):
        self._isTargetReached = True

    def isTargetReached(self):
        return self._isTargetReached

    def setAnswer(self, value):
        self._answer = value

    def getAnswer(self):
        return self._answer

    def hasBeenAnswered(self):
        return self._answer != None

    def getPatient(self):
        return self._patient

    def __str__(self):
        return


class PlanVerificator:
    def __str__(self):
        return


class PlanConditioner:
    def __str__(self):
        return


class Planner:
    def __init__(self, robot):
        self.robot = robot
        self.planner = self.robot.world.createPlanner()
        self.medical_room = next(
            x for x in self.robot.world.rooms if "medical" in x.name.lower())
        self.currentStep = None
        self.currentPath = []
        self.steps = []

    def reset(self):
        # Standard steps
        self.steps = [
            PlanStep.none(),
            PlanStep(self.medical_room.door, Activity.MOVING,
                     "Going to the Medical Room for taking the pills"),
            PlanStep(None, Activity.TAKE_PILLS, None, lambda: (
                self.robot.setPills(self.robot.world.patientsCount()),
            )),
            PlanStep(self.robot.base, Activity.MOVING, str(
                self.robot.world.patientsCount()) + " pills taken"),
            PlanStep.none(),
        ]

        # Patient based steps
        for p in self.robot.world.patientsList():
            status1 = "Going to " + p.name + " Room"
            status2 = p.name + ", can I enter?"
            self.steps.extend([
                PlanStep(p.room.door, Activity.MOVING, status1, patient=p),
                PlanStep(None, Activity.WAIT_ANSWER, status2, patient=p),
                PlanStep(p.room.door, Activity.MOVING, patient=p),
            ])

        # Standard steps
        self.steps.extend([
            PlanStep(self.robot.base, Activity.MOVING, "Going to the Base"),
            PlanStep(None, Activity.NONE,
                     "All the tasks completed for today. See you tomorrow!"),
        ])

    def isWaitingAnswer(self):
        return self.currentStep is not None and self.currentStep.activity == Activity.WAIT_ANSWER

    def setAnswer(self, answer):
        if self.currentStep is not None and self.currentStep.activity == Activity.WAIT_ANSWER:
            self.currentStep.setAnswer(answer)

    def currentActivity(self):
        if self.currentStep is not None:
            return self.currentStep.activity
        return Activity.NONE

    def process(self):
        if self.steps:
            if self.currentStep is None:
                self.currentStep = self.steps.pop(0)

                if self.currentStep.status is not None:
                    self.robot.setStatus(self.currentStep.status)
                else:
                    self.robot.setStatus("")

                # Compute the path from robot actual position to the target
                if self.currentStep.target is not None:
                    self.currentPath = self.compute_path(
                        self.currentStep.target)

            else:
                if self.currentStep.activity != Activity.WAIT_ANSWER:
                    if len(self.currentPath) > 0:
                        p = self.currentPath.pop(0)
                        if len(self.currentPath) > 0:
                            self.currentPath.pop(0)
                        return p
                    else:
                        self.currentStep.targetReached()

                    # I've reached the point => I can execute the callback (if any)
                    if self.currentStep.isTargetReached():
                        if self.currentStep.onComplete is not None:
                            self.currentStep.onComplete()
                        self.currentStep = None
                else:
                    if self.currentStep.hasBeenAnswered():
                        answer = self.currentStep.getAnswer()
                        patient = self.currentStep.getPatient()
                        if patient is not None:
                            # TODO: prepend tasks to self.steps according user profile (use verificator and/or conditioner)
                            if answer:
                                # The patient said Yes
                                self.robot.conversation = "Yes"
                                self.activity = Activity.PATIENT_GIVE_PILL
                                self.steps.insert(
                                    0,
                                    PlanStep(
                                        patient.position,
                                        Activity.PATIENT_GIVE_PILL,
                                        "Entering into " + patient.name + "'s room",
                                        patient=patient,
                                        onComplete=lambda: (
                                            self.robot.setConversation(""),
                                        )
                                    )
                                )
                            else:
                                # The patiend said No
                                self.steps = [
                                    s for s in self.steps if s.getPatient() != patient
                                ]
                                self.robot.conversation = "No"
                                self.steps.insert(
                                    0,
                                    PlanStep(
                                        self.robot.world.findPlayer(
                                            "nurse").position,
                                        Activity.CALL_NURSE_FOR_PATIENT,
                                        "Call Nurse for " + patient.name,
                                        onComplete=lambda: (
                                            self.robot.setConversation(""),
                                        )
                                    )
                                )
                                pass

                        if self.currentStep.onComplete is not None:
                            self.currentStep.onComplete()
                        self.currentStep = None
        return None

    def compute_path(self, target):
        return self.robot.world.findPath(self.robot.world, self.planner, self.robot.model.position, target)

    def __str__(self):
        return ""


class Robot:

    def __init__(self, model, world, xml_configuration_file=""):
        self.model = model
        self.world = world
        self.reset()
        
        if xml_configuration_file:
            self.configuration = Configurer().load_configuration(xml_configuration_file)
            if (self.configuration):
                Logger.s(f"Configuration loaded for Robot with Id: {self.configuration.get_id()} ")

    def reset(self):
        self.model.position = self.world.robotBaseCoords()
        self._delta = Constants.ROBOT_INITIAL_DELTA
        self.step = 0
        self.status = ""
        self.conversation = ""
        self.pills = Constants.ROBOT_INITIAL_NUMBER_OF_PILLS
        self.base = self.world.robotBaseCoords()
        self.planner = Planner(self)

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

    def startDailyActivities(self):
        self.planner.reset()

    def update(self, dt=0, status_text=None, conversation_text=None):
        status_text.text = self.status
        conversation_text.text = self.conversation

        p = self.planner.process()
        if p is not None:
            origin = self.model.world_position
            ignore = [self.model]
            # ignore.extend(self.world.players)
            hit_info = raycast(origin, Vec3(p.x, p.y, 0), ignore=ignore, distance=1, debug=False)
            if not hit_info.hit:
                self.model.position = (p.x, p.y, 0)

    def isWaitingAnswer(self):
        return self.planner.isWaitingAnswer()

    def setAnswer(self, answer):
        self.planner.setAnswer(answer)

    def interactWith(self, model):
        if self.planner.currentActivity() == Activity.PATIENT_GIVE_PILL:
            self.pills -= 1
            self.status = "Pills taken!, Pill delivered to " + model.name
        else:
            self.conversation = "Hi " + model.name + "!"
