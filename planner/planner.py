from logger import Logger
from . import actions as a
from .conditioner import *
from .verificator import *
import py_trees
import operator
from patient_utils import get_items_from_patient_configuration
import copy

class Planner:
    def __init__(self, robot):
        self.planConditioners = {"pill_attempts": PlanConditioner(0)}
        self.planVerificators = {"patient_humor": PlanVerificator(robot.configuration)}
        self.robot = robot
        self.planner = self.robot.world.createPlanner()
        self.medical_room = next(
            x for x in self.robot.world.rooms if "medical" in x.name.lower()
        )
        self.currentStep = None
        self.currentPath = []
        self.steps = []
        self.behaviour_tree = None
        self.blackboard = py_trees.blackboard.Blackboard()
        for p in self.robot.world.patientsList():
            self.blackboard.set(f"{p.name.lower()}_can_enter", False)
            self.blackboard.set(f"{p.name.lower()}_has_distress", False)
            self.blackboard.set(f"{p.name.lower()}_guardian_answered", False)

    def reset(self):
        # Standard steps
        start_root = py_trees.composites.Sequence("Daily Jobs", memory=True)
        start_root.add_children(
            [
                py_trees.composites.Sequence(
                    "Go to medical room",
                    memory=True,
                ).add_children(
                    [
                        a.MovingAction(
                            name="Moving to Medical Room",
                            planner=self,
                            target=self.medical_room.door,
                        ),
                        a.MovingAction(
                            name="Taking the Pills",
                            planner=self,
                            target=self.medical_room.center,
                        ),
                        a.ExecutionAction(
                            name="Taken Pills",
                            onComplete=lambda: (
                                self.robot.setPills(self.robot.world.patientsCount()),
                            ),
                        ),
                        a.MovingAction(
                            name="Exiting from Medical Room",
                            planner=self,
                            target=self.medical_room.door,
                        ),
                        a.MovingAction(
                            name="Going back to base",
                            planner=self,
                            target=self.robot.base,
                        ),
                    ]
                ),
            ]
        )

        # Patient based steps
        for p in self.robot.world.patientsList():
            step_can_enter = py_trees.composites.Sequence(
                f"{p.name} can enter",
                memory=True,
            )
            step_cannot_enter = py_trees.composites.Sequence(
                f"{p.name} cannot enter",
                memory=True,
            )
            step_cannot_enter.add_children(
                [
                    a.MovingAction(
                        name=f"Leaving {p.name}'s Room",
                        planner=self,
                        patient=p,
                        target=p.room.door,
                    ),
                    a.MovingAction(
                        name="Calling the nurse",
                        planner=self,
                        patient=p,
                        target=self.robot.world.findPlayer("nurse").position,
                    ),
                    a.MovingAction(
                        name="Going back to base", planner=self, target=self.robot.base
                    ),
                ]
            ),

            patient_items = get_items_from_patient_configuration(p.patientConfiguration)
            if (
                patient_items["autonomy_rule_accept_health_status_check"] is not None
                and
                patient_items["autonomy_rule_accept_health_status_check"].value == "true"
            ):
                step2 = py_trees.composites.Sequence(
                    f"Step 2 {p.name}",
                    memory=True,
                )
                if patient_items["autonomy_action_do_call_legal_guardian"] is not None:
                    step3 = py_trees.composites.Sequence(
                        f"Step 3 {p.name}",
                        memory=True,
                    ).add_children(
                        [
                            a.ExecutionAction(
                                name=f"{p.name} legal guardian answered",
                                onComplete=lambda: (),
                            ),
                            a.MovingAction(
                                name=f"Going out from {p.name}'s Room",
                                planner=self,
                                patient=p,
                                target=p.room.door,
                            ),
                            a.MovingAction(
                                name="Going back to base",
                                planner=self,
                                target=self.robot.base,
                            ),
                        ]
                    )
                else:
                    step2 = copy.copy(step_cannot_enter)

            if (
                patient_items["privacy_rule_accept_recording"] is not None
                and patient_items["privacy_rule_accept_recording"].value == "true"
            ):
                if patient_items["privacy_exception_patient_is_in_toilet"] is not None:
                    step_can_enter.add_child(
                        a.ExecutionAction(
                            name=f"Check if {p.name} is in Toilet",
                            onComplete=lambda: (
                                self.robot.setRecording(random.randint(0, 1) == 1)
                            ),
                        )
                    )

            if (
                patient_items["autonomy_rule_accept_medication_reminder"] is not None
                and
                patient_items["autonomy_rule_accept_medication_reminder"].value == "true"
            ):

                def add_pill_reminder(force):
                    if force:
                        step_can_enter.add_child(
                            a.ExecutionAction(
                                name=f"{p.name}, you should take the pill!",
                                onComplete=lambda: (),
                            )
                        )

                add_pill_reminder(force=True)

                if patient_items["autonomy_exception_enough_repetition"] is not None:
                    step_can_enter.add_child(
                        a.ExecutionAction(
                            name=f"Enough repetitions...",
                            onComplete=lambda: (
                                add_pill_reminder(force=(random.randint(0, 1) == 1))
                            ),
                        ),
                    )

            if (
                patient_items["dignity_rule_accept_ambulatory_support"] is not None
                and
                patient_items["dignity_rule_accept_ambulatory_support"].value == "true"
            ):
                step_can_enter.add_children(
                    [
                        a.MovingAction(
                            name=f"Starting check {p.name} health status",
                            planner=self,
                            patient=p,
                            target=p.position,
                        ),
                        a.ExecutionAction(
                            name=f"Finished check {p.name} health status",
                            onComplete=lambda: (
                                self.blackboard.set(
                                    p.name.lower() + "_has_distress",
                                    random.randint(0, 1) == 1,
                                ),
                            ),
                        ),
                        py_trees.idioms.either_or(
                            name="Evaluating health status",
                            conditions=[
                                py_trees.common.ComparisonExpression(
                                    p.name.lower() + "_has_distress", False, operator.eq
                                ),
                                py_trees.common.ComparisonExpression(
                                    p.name.lower() + "_has_distress", True, operator.eq
                                ),
                            ],
                            subtrees=[
                                py_trees.composites.Sequence(
                                    f"{p.name} not stressed",
                                    memory=True,
                                ).add_children(
                                    [
                                        a.ExecutionAction(
                                            name=f"Preparing the {p.name}'s pill",
                                            onComplete=lambda: (
                                            ),
                                        ),
                                        a.MovingAction(
                                            name=f"Give the pill to {p.name}",
                                            planner=self,
                                            patient=p,
                                            target=p.position,
                                        ),
                                        a.ExecutionAction(
                                            name=f"{p.name} has taken the pill",
                                            onComplete=lambda: (
                                                self.robot.decreasePills(),
                                            ),
                                        ),
                                        a.MovingAction(
                                            name=f"Exiting from {p.name}'s Room",
                                            planner=self,
                                            patient=p,
                                            target=p.room.door,
                                        )
                                    ]
                                ),
                                py_trees.composites.Sequence(
                                    f"{p.name} stressed",
                                    memory=True,
                                ).add_children(
                                    [
                                        a.ExecutionAction(
                                            name="Check Legal Guardian",
                                            onComplete=lambda: (
                                                step2.add_children(
                                                    [
                                                        a.ExecutionAction(
                                                            name=f"Calling {p.name}'s legal guardian",
                                                            onComplete=lambda: (
                                                                self.blackboard.set(
                                                                    f"{p.name.lower()}_guardian_answered",
                                                                    random.randint(0, 1) == 1
                                                                )
                                                            ),
                                                        ),
                                                        py_trees.idioms.either_or(
                                                            name="Guardian Answered",
                                                            conditions=[
                                                                py_trees.common.ComparisonExpression(
                                                                    f"{p.name.lower()}_guardian_answered",
                                                                    True,
                                                                    operator.eq,
                                                                ),
                                                                py_trees.common.ComparisonExpression(
                                                                    f"{p.name.lower()}_guardian_answered",
                                                                    False,
                                                                    operator.eq,
                                                                ),
                                                            ],
                                                            subtrees=[
                                                                step3,
                                                                copy.copy(
                                                                    step_cannot_enter
                                                                ),
                                                            ],
                                                        ),
                                                    ]
                                                )
                                            ),
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        copy.copy(step2),
                    ]
                ),

            self.robot.patientPlan[p] = py_trees.composites.Sequence(
                f"Visiting {p.name}",
                memory=True,
            ).add_children(
                [
                    a.MovingAction(
                        name=f"Going to {p.name}'s room",
                        planner=self,
                        patient=p,
                        target=p.room.door,
                    ),
                    a.ExecutionAction(
                        name=f"Beginning the process of configuring {p.name} privacy rules",
                        onComplete=lambda: (
                            self.robot.configureSensorAccordingPatientPrivacy(
                                patient_items
                            )
                        )
                    ),
                    a.ExecutionAction(
                        name=f"Finished the process of configuring {p.name} privacy rules",
                        onComplete=lambda: (
                            self.robot.configureSensorAccordingPatientPrivacy(
                                patient_items
                            )
                        )
                    ),
                    a.InteractionAction(
                        name=f"{p.name}, can I enter?",
                        planner=self,
                        patient=p,
                        onComplete=lambda: (),
                    ),
                    py_trees.idioms.either_or(
                        name=f"Start interaction with {p.name}",
                        conditions=[
                            py_trees.common.ComparisonExpression(
                                p.name.lower() + "_can_enter", True, operator.eq
                            ),
                            py_trees.common.ComparisonExpression(
                                p.name.lower() + "_can_enter", False, operator.eq
                            ),
                        ],
                        subtrees=[
                            step_can_enter,
                            copy.copy(step_cannot_enter),
                        ],
                    ),
                ]
            )
            start_root.add_children([self.robot.patientPlan[p]])

        # Standard steps
        start_root.add_children(
            [
                py_trees.composites.Sequence(
                    "Daily tasks completed",
                    memory=True,
                ).add_children(
                    [
                        a.MovingAction(
                            name="Going to the Base",
                            planner=self,
                            target=self.robot.base,
                        ),
                        a.ExecutionAction(
                            name="Going to sleep",
                            onComplete=lambda: (
                                self.processCompleted(),
                                self.robot.setStatus(
                                    "All the tasks completed for today. See you tomorrow!"
                                ),
                            ),
                        ),
                    ]
                ),
            ]
        )

        self.behaviour_tree = py_trees.trees.BehaviourTree(root=start_root)
        py_trees.display.render_dot_tree(
            start_root,
            target_directory="./images",
        )
        self.behaviour_tree.setup(timeout=15)

    def isWaitingAnswer(self):
        return self.currentStep is not None and isinstance(
            self.currentStep, a.InteractionAction
        )

    def setAnswer(self, answer):
        if self.currentStep is not None and isinstance(
            self.currentStep, a.InteractionAction
        ):
            self.currentStep.setAnswer(answer)

    def processCompleted(self):
        if self.behaviour_tree is not None:
            self.behaviour_tree.interrupt(),
            self.behaviour_tree.shutdown(),
            self.behaviour_tree = None

    def process(self):
        def print_tree(tree):
            print(py_trees.display.unicode_tree(root=tree.root, show_status=True))

        if self.behaviour_tree is not None:
            try:
                self.behaviour_tree.tick(
                    pre_tick_handler=None,
                    # post_tick_handler=print_tree
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
        return self.robot.world.findPath(
            self.robot.world, self.planner, self.robot.model.position, target
        )

    def __str__(self):
        return ""
