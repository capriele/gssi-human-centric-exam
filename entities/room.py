
class Room:
    def __init__(self, name, door, polygon):
        self.name = name
        self.door = door
        self.polygon = polygon

    def __str__(self):
        return self.name
