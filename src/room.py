import scene

# Represent node room which represents a undirected graph between different scenes
class Room():
    def __init__(self):
        self.scene = None
        self.neighbours = {}
