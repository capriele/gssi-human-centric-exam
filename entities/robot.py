from ursina import *

from constants import Constants
from logger import Logger

from planner import *


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
        self.patientPlan = dict()
        self.recording = True
        self.distribution = True
        self.storage = True

    def configureSensorAccordingPatientPrivacy(self, items):
        if items['privacy_rule_accept_recording'] is not None:
            self.recording = items['privacy_rule_accept_recording']
        else:
            self.recording = True

        if items['privacy_rule_accept_distribution'] is not None:
            self.distribution = items['privacy_rule_accept_distribution']
        else:
            self.distribution = True

        if items['privacy_rule_accept_storage'] is not None:
            self.storage = items['privacy_rule_accept_storage']
        else:
            self.storage = True

    def setRecording(self, recording):
        self.recording = recording

    def setDistribution(self, distribution):
        self.distribution = distribution

    def setStorage(self, storage):
        self.storage = storage

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
