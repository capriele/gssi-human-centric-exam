import random


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
