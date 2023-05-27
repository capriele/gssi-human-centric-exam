from configurer import Configurer
from constants import Constants
from logger import Logger

from . import actions as a
from .conditioner import *
from .verificator import *
import py_trees
import operator


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
                a.MovingAction(
                    name="Moving to Medical Room",
                    planner=self,
                    target=self.medical_room.door
                ),
                a.MovingAction(
                    name="Moving to Medical Room",
                    planner=self,
                    target=self.medical_room.center
                ),
                a.ExecutionAction(
                    name="Take Pills",
                    onComplete=lambda: (
                        print("Pills Taken"),
                        self.robot.setPills(self.robot.world.patientsCount()),
                    ),
                ),
                a.MovingAction(
                    name="Exiting from Medical Room",
                    planner=self,
                    target=self.medical_room.door
                ),
                a.MovingAction(
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
                    a.MovingAction(
                        name="Going to " + p.name + " Room",
                        planner=self,
                        patient=p,
                        target=p.room.door,
                    ),
                    a.InteractionAction(
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
                                a.MovingAction(
                                    name="Give pill to " + p.name,
                                    planner=self,
                                    patient=p,
                                    target=p.position,
                                ),
                                a.ExecutionAction(
                                    name=p.name + " takes the pill",
                                    onComplete=lambda: (
                                        self.robot.decreasePills(),
                                    ),
                                ),
                                a.MovingAction(
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
                                a.MovingAction(
                                    name="Calling the nurse",
                                    planner=self,
                                    patient=p,
                                    target=self.robot.world.findPlayer(
                                        "nurse").position,
                                ),
                                a.MovingAction(
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
                a.MovingAction(
                    name="Going to the Base",
                    planner=self,
                    target=self.robot.base
                ),
                a.ExecutionAction(
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
        return self.currentStep is not None and isinstance(self.currentStep, a.InteractionAction)

    def setAnswer(self, answer):
        if self.currentStep is not None and isinstance(self.currentStep, a.InteractionAction):
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
