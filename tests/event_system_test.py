import sys

sys.path.insert(1, 'core')
import core

class Collision_event(core.Event):
    def __init__(self, entity1, entity2):
         self.entity1 = entity1
         self.entity2 = entity2

def on_collision(event):
    print(event)

event_system = core.Event_system()
event_system.subscribe_event(Collision_event("entity1", "entity3"), on_collision)
event_system.dispatch_event(Collision_event("entity1", "entity2"))
event_system.dispatch_event(Collision_event("entity1", "entity3"))