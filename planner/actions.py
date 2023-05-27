from ursina import *
import py_trees
from shapely.geometry import Point
import time
import uuid
from .planner import *

from configurer import Configurer
from constants import Constants
from logger import Logger


class MovingAction(py_trees.behaviour.Behaviour):

    def __init__(self, name: str, planner: Planner, target: Point, patient=None, onComplete=None):
        """Configure the name of the behaviour."""
        super(MovingAction, self).__init__(name)
        self.id = (
            uuid.uuid4()
        )
        self.status = py_trees.common.Status.RUNNING
        self.planner = planner
        self.patient = patient
        self.target = target
        self.onComplete = onComplete
        self.path = []

    def setup(self, **kwargs: int) -> None:
        pass

    def initialise(self) -> None:
        self.path = self.planner.compute_path(self.target)

    def update(self) -> py_trees.common.Status:
        """Increment the counter, monitor and decide on a new status."""
        new_status = py_trees.common.Status.RUNNING
        if self.status != py_trees.common.Status.SUCCESS:
            if self.path:
                p = self.path.pop(0)
                for i in range(0, 5):
                    if len(self.path) > 0:
                        self.path.pop(0)
                if p is not None:
                    origin = self.planner.robot.model.world_position
                    ignore = [self.planner.robot.model]
                    # ignore.extend(self.world.players)
                    # ignore.extend(self.world.walls)
                    hit_info = raycast(origin, Vec3(p.x, p.y, 0),
                                       ignore=ignore, distance=1, debug=False)
                    if not hit_info.hit:
                        self.planner.robot.model.position = (p.x, p.y, 0)
                new_status = py_trees.common.Status.RUNNING
            else:
                new_status = py_trees.common.Status.SUCCESS
                if self.onComplete is not None:
                    self.onComplete()
        return new_status


class ExecutionAction(py_trees.behaviour.Behaviour):

    def __init__(self, name: str, onComplete=None):
        """Configure the name of the behaviour."""
        super(ExecutionAction, self).__init__(name)
        self.id = (
            uuid.uuid4()
        )
        self.status = py_trees.common.Status.RUNNING
        self.onComplete = onComplete
        self.startTime = time.time()

    def initialise(self) -> None:
        self.startTime = time.time()

    def update(self) -> py_trees.common.Status:
        """Increment the counter, monitor and decide on a new status."""
        new_status = py_trees.common.Status.RUNNING
        if self.status != py_trees.common.Status.SUCCESS:
            if (time.time() - self.startTime) > Constants.ROBOT_EXECUTION_ACTION_DT:
                if self.onComplete is not None:
                    self.onComplete()
                    new_status = py_trees.common.Status.SUCCESS
                else:
                    new_status = py_trees.common.Status.FAILURE
        return new_status


class InteractionAction(py_trees.behaviour.Behaviour):

    def __init__(self, name: str, planner: Planner = None, patient=None, onComplete=None):
        """Configure the name of the behaviour."""
        super(InteractionAction, self).__init__(name)
        self.id = (
            uuid.uuid4()
        )
        self.status = py_trees.common.Status.INVALID
        self.patient = patient
        self.onComplete = onComplete
        self._answer = None
        self.planner = planner
        self.blackboard = self.planner.blackboard
        self.startTime = time.time()

    def initialise(self) -> None:
        self.planner.robot.conversation = ""
        self.startTime = time.time()

    def setAnswer(self, answer):
        self._answer = answer

    def getAnswer(self):
        return self._answer

    def getStatus(self):
        tentative = self.planner.planConditioners['pill_attempts'].status + 1
        status = self.name + " [Tentative: " + str(tentative) + "]"
        return status

    def update(self) -> py_trees.common.Status:
        """Increment the counter, monitor and decide on a new status."""

        new_status = py_trees.common.Status.RUNNING
        if self.status != py_trees.common.Status.SUCCESS:
            if self._answer is not None and (time.time() - self.startTime) > Constants.TIMEOUT_IN_SECONDS_TO_PATIENT_INTERACTION:
                self.startTime = time.time()

                if self._answer:
                    # The patient said Yes
                    new_status = py_trees.common.Status.SUCCESS
                    self.planner.robot.conversation = Constants.ANSWER_YES
                    self.planner.planConditioners["pill_attempts"].reset()
                    if self.blackboard is not None:
                        self.blackboard.set(
                            self.patient.name.lower()+"_can_enter",
                            self._answer
                        )
                else:
                    # The patient said No
                    if self.planner.planConditioners['pill_attempts'].status + 1 > 1:
                        self.planner.robot.conversation += ", "
                    self.planner.robot.conversation += Constants.ANSWER_NO
                    self.planner.robot.conversation = self.planner.robot.conversation.rstrip(
                        ',')
                    patientHumorConfiguration = self.planner.robot.configuration.get_properties().get_property()[
                        0]
                    patientHumor = self.planner.planConditioners["pill_attempts"].random(
                        patientHumorConfiguration.from_, patientHumorConfiguration.to)
                    Logger.i(f"Patient Humor Score: {patientHumor}")

                    self.planner.planConditioners["pill_attempts"].inc()
                    self.blackboard.set(
                        self.patient.name.lower()+"_pill_attempts",
                        self.planner.planConditioners['pill_attempts'].status + 1
                    )
                    Logger.i(
                        f"Number of attempts: {self.planner.planConditioners['pill_attempts'].status + 1}")
                    if self.planner.planVerificators["patient_humor"].verify(["patient_humor_good", "patient_humor_bad"], patientHumor, self.planner.planConditioners["pill_attempts"].status):
                        self._answer = None
                    else:
                        new_status = py_trees.common.Status.SUCCESS
                        self.planner.planConditioners["pill_attempts"].reset()
                        if self.blackboard is not None:
                            self.blackboard.set(
                                self.patient.name.lower()+"_can_enter",
                                self._answer
                            )

                if self.onComplete is not None:
                    self.onComplete()
        return new_status


if __name__ == '__main__':
    root = py_trees.composites.Sequence("Daily Jobs", memory=False)
    med = py_trees.behaviours.Success(name="Med Priority")
    low = py_trees.behaviours.Success(name="Low Priority")
    root.add_children([
        py_trees.composites.Sequence(
            "Go to medical room",
            memory=True,
        ).add_children([
            MovingAction(
                name="Moving to Medical Room",
                target=Point(10, 10)
            ),
            ExecutionAction(
                name="Take Pills",
                onComplete=lambda: (print("Pills Taken"))
            ),
            MovingAction(
                name="Going back to base",
                target=Point(1, 1)
            ),
        ]),
        med,
        low
    ])

    behaviour_tree = py_trees.trees.BehaviourTree(
        root=root
    )
    py_trees.display.render_dot_tree(root)
    behaviour_tree.setup(timeout=15)

    def print_tree(tree):
        print(py_trees.display.unicode_tree(root=tree.root, show_status=True))

    try:
        behaviour_tree.tick_tock(
            period_ms=300,
            number_of_iterations=py_trees.trees.CONTINUOUS_TICK_TOCK,
            pre_tick_handler=None,
            post_tick_handler=print_tree
        )
    except KeyboardInterrupt:
        behaviour_tree.interrupt()
