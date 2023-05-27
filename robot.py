from ursina import *
from enum import Enum
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from configurer import Configurer
from constants import Constants
from logger import Logger

from actions import *
import py_trees
import operator


class PlanVerificator:
    def __init__(self, configuration):
        self.configuration = configuration

    def verify(self, properties, patient_value, robot_value):
        filtered_properties = [property for property in self.configuration.get_properties(
        ).get_property() if property.key in properties]
        for property in filtered_properties:
            if property.from_ <= patient_value and patient_value <= property.to:
                Logger.i(f"Verifying the property if_{property.key}...")
                return robot_value <= [behaviour for behaviour in self.configuration.get_behaviours().get_behaviour() if behaviour.key in ["if_" + property.key]][0].value

    def __str__(self):
        return


class PlanConditioner:

    def __init__(self, status=0):
        self.status = status

    def inc(self, value=1):
        self.status += value

    def dec(self, value=1):
        self.status -= value

    def reset(self):
        self.status = 0

    def random(self, _from, to):
        return random.randint(_from, to)

    def __str__(self):
        return


class Planner:
    def __init__(self, robot):
        self.planConditioners = {"pill_attempts": PlanConditioner(0)}
        self.planVerificators = {
            "patient_humor": PlanVerificator(robot.configuration)}
        self.robot = robot
        self.planner = self.robot.world.createPlanner()
        self.medical_room = next(
            x for x in self.robot.world.rooms if "medical" in x.name.lower())
        self.currentStep = None
        self.currentPath = []
        self.steps = []
        self.behaviour_tree = None
        self.blackboard = py_trees.blackboard.Blackboard()
        for p in self.robot.world.patientsList():
            self.blackboard.set(p.name.lower()+"_can_enter", False)

    def reset(self):
        # Standard steps
        start_root = py_trees.composites.Sequence("Daily Jobs", memory=True)
        start_root.add_children([
            py_trees.composites.Sequence(
                "Go to medical room",
                memory=True,
            ).add_children([
                MovingAction(
                    name="Moving to Medical Room",
                    planner=self,
                    target=self.medical_room.door
                ),
                ExecutionAction(
                    name="Take Pills",
                    onComplete=lambda: (
                        print("Pills Taken"),
                        self.robot.setPills(self.robot.world.patientsCount()),
                    ),
                ),
                MovingAction(
                    name="Going back to base",
                    planner=self,
                    target=self.robot.base
                ),
            ]),
        ])

        # Patient based steps
        for p in self.robot.world.patientsList():
            start_root.add_children([
                py_trees.composites.Sequence(
                    "Visiting " + p.name,
                    memory=True,
                ).add_children([
                    MovingAction(
                        name="Going to " + p.name + " Room",
                        planner=self,
                        patient=p,
                        target=p.room.door,
                    ),
                    InteractionAction(
                        name=p.name + ", can I enter?",
                        planner=self,
                        patient=p,
                        onComplete=lambda: (),
                    ),
                    py_trees.idioms.either_or(
                        name="Interacting with " + p.name,
                        conditions=[
                            py_trees.common.ComparisonExpression(
                                p.name.lower()+"_can_enter", True, operator.eq),
                            py_trees.common.ComparisonExpression(
                                p.name.lower()+"_can_enter", False, operator.eq),
                        ],
                        subtrees=[
                            py_trees.composites.Sequence(
                                "Visiting " + p.name,
                                memory=True,
                            ).add_children([
                                MovingAction(
                                    name="Give pill to " + p.name,
                                    planner=self,
                                    patient=p,
                                    target=p.position,
                                ),
                                ExecutionAction(
                                    name=p.name + " takes the pill",
                                    onComplete=lambda: (
                                        self.robot.decreasePills(),
                                    ),
                                ),
                                MovingAction(
                                    name="Exiting from " + p.name + " Room",
                                    planner=self,
                                    patient=p,
                                    target=p.room.door,
                                ),
                            ]),
                            py_trees.composites.Sequence(
                                "Visiting " + p.name,
                                memory=True,
                            ).add_children([
                                MovingAction(
                                    name="Calling the nurse",
                                    planner=self,
                                    patient=p,
                                    target=self.robot.world.findPlayer(
                                        "nurse").position,
                                ),
                                MovingAction(
                                    name="Going back to base",
                                    planner=self,
                                    target=self.robot.base
                                ),
                            ]),
                        ],
                        namespace=p.name.lower()+"_either_or",
                    ),
                ])
            ])

        # Standard steps
        start_root.add_children([
            py_trees.composites.Sequence(
                "Daily tasks completed",
                memory=True,
            ).add_children([
                MovingAction(
                    name="Going to the Base",
                    planner=self,
                    target=self.robot.base
                ),
                ExecutionAction(
                    name="Going to sleep",
                    onComplete=lambda: (
                        self.processCompleted(),
                        self.robot.setStatus(
                            "All the tasks completed for today. See you tomorrow!"),
                    ),
                ),
            ]),
        ])

        self.behaviour_tree = py_trees.trees.BehaviourTree(
            root=start_root
        )
        py_trees.display.render_dot_tree(
            start_root,
            target_directory="./images",
        )
        self.behaviour_tree.setup(timeout=15)

    def isWaitingAnswer(self):
        return self.currentStep is not None and isinstance(self.currentStep, InteractionAction)

    def setAnswer(self, answer):
        if self.currentStep is not None and isinstance(self.currentStep, InteractionAction):
            self.currentStep.setAnswer(answer)

    def processCompleted(self):
        if self.behaviour_tree is not None:
            self.behaviour_tree.interrupt(),
            self.behaviour_tree.shutdown(),
            self.behaviour_tree = None

    def process(self):
        def print_tree(tree):
            print(py_trees.display.unicode_tree(
                root=tree.root, show_status=True))
        if self.behaviour_tree is not None:
            try:
                self.behaviour_tree.tick(
                    pre_tick_handler=None,
                    post_tick_handler=print_tree
                )
                self.currentStep = self.behaviour_tree.tip()
                if self.currentStep:
                    try:
                        status = self.currentStep.getStatus()
                    except:
                        status = self.currentStep.name
                    if self.currentStep.parent:
                        status = self.currentStep.parent.name + " > " + status
                    self.robot.setStatus(status)
            except:
                pass
            return self.currentStep
        return None

    def compute_path(self, target):
        return self.robot.world.findPath(self.robot.world, self.planner, self.robot.model.position, target)

    def __str__(self):
        return ""


class Robot:

    def __init__(self, model, world, configuration=None):
        self.model = model
        self.world = world

        if configuration:
            self.configuration = configuration
            Logger.s(
                f"Configuration loaded for Robot with Id: {self.configuration.get_id()} ")

        self.reset()

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

    def setPills(self, num):
        self.pills = num

    def decreasePills(self):
        if self.pills > 0:
            self.pills -= 1

    def setStatus(self, text):
        self.status = text

    def setConversation(self, text):
        self.conversation = text

    def startDailyActivities(self):
        self.planner.reset()

    def update(self, dt=0, status_text=None, conversation_text=None):
        status_text.text = self.status
        conversation_text.text = self.conversation

        self.planner.process()

    def isWaitingAnswer(self):
        return self.planner.isWaitingAnswer()

    def setAnswer(self, answer):
        self.planner.setAnswer(answer)

    def interactWith(self, model):
        self.conversation = "Hi " + model.name + "!"
