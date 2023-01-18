import core.core as core

class Finished_event(core.Component):
    def __init__(self, entity, component):
        self.entity = entity
        self.component = component

class Trigger_event(core.Event):
    def __init__(self, entity, trigger_type):
        self.entity = entity
        self.trigger_type

class Add_component_event(core.Event):
    def __init__(self, component_type, entity):
        self.component_type = component_type
        self.entity = entity

class Tick_event(core.Event):
    pass

class Collision_event(core.Event):
    def __init__(self, entity1, entity2):
        super().__init__()
        self.entity1 = entity1
        self.entity2 = entity2

class Delay_event(core.Event):
    def __init__(self, action, delay):
        self.action = action
        self.delay = delay

class Cleanup_event(core.Event):
    pass

class Destroy_entity_event(core.Event):
    def __init__(self, entity):
        self.entity = entity

class Target_event(core.Event):
    def __init__(self, entity):
        self.entity = entity

# ========== DEBUG =================00

class Log_event(core.Event):
    def __init__(self, key, value):
        super().__init__()
        self.key = key 
        self.value = value