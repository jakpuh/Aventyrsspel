import core.core as core

class Print_event(core.Component):
    def __init__(self, key, value, right_sidebar: bool):
        self.key = key 
        self.value = value
        self.right_sidebar = right_sidebar

# When a entity kills another entity
class Hit_event(core.Component):
    def __init__(self, attacker_entity, victim_entity):
        self.attacker_entity = attacker_entity
        self.victim_entity = victim_entity

# Resets the state of a entity which a system has been modifing
class Reset_event(core.Component):
    def __init__(self, entity, component):
        self.component = component
        self.entity = entity

# Disabled and enable the children of an entity
class Set_children_state_event(core.Component):
    DISABLE = 0
    ENABLE = 1

    def __init__(self, entity, state):
        self.entity = entity
        self.state = state

# Maybe create a message event instead
# When a system is finished (e.i dashing hits the playre)
class Finished_event(core.Component):
    def __init__(self, entity, component):
        self.entity = entity
        self.component = component

# Triggers an action
class Trigger_event(core.Event):
    def __init__(self, entity, trigger_type):
        self.entity = entity
        self.trigger_type = trigger_type

# When a component is added to an entity
class Add_component_event(core.Event):
    def __init__(self, component_type, entity):
        self.component_type = component_type
        self.entity = entity

# Sends every tick
class Tick_event(core.Event):
    pass

# When 2 entities collide
class Collision_event(core.Event):
    def __init__(self, entity1, entity2):
        super().__init__()
        self.entity1 = entity1
        self.entity2 = entity2

# Delays an action
class Delay_event(core.Event):
    def __init__(self, action, delay):
        self.action = action
        self.delay = delay

# Cleanup the scene
class Cleanup_event(core.Event):
    pass

# Destroy the entity
class Destroy_entity_event(core.Event):
    def __init__(self, entity):
        self.entity = entity

# Specifies a new target for the entity
class Target_event(core.Event):
    def __init__(self, entity):
        self.entity = entity

# ========== DEBUG =================00
class Log_event(core.Event):
    def __init__(self, key, value):
        super().__init__()
        self.key = key 
        self.value = value