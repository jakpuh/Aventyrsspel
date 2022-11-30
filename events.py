import sys

sys.path.insert(1, 'core')
import core 

class Tick_event(core.Event):
    pass

class Collision_event(core.Event):
    def __init__(self, entity1, entity2) :
        super().__init__()
        self.entity1 = entity1
        self.entity2 = entity2