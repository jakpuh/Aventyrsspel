import core.core as core
import math

class C_disable(core.Component):
    pass

class C_normal_trigger(core.Component):
    def __init__(self, sensitivity = 0):
        self.sensitivity = sensitivity
        self.ticks_since_last_trigger = 0

class C_target(core.Component):
    def __init__(self, target):
        self.target = target

class C_xp(core.Component):
    def __init__(self, xp):
        self.xp = xp

class C_boss_game_manager(core.Component):
    def __init__(self, action):
        self.action = action

    
class C_delay(core.Component):
    def __init__(self, actions: list[tuple[2]] = [], named_actions: dict = {}):
        self.named_actions = named_actions
        self.actions = actions

class C_thorn():
    def __init__(self, damage, invinc_ticks = 21):
        self.damage = damage
        self.invinc_ticks = invinc_ticks

class C_impenetrable():
    pass

class C_health(core.Component):
    def __init__(self, health):
        self.health = health  

class C_lifetime(core.Component):
    def __init__(self, lifetime):
        self.lifetime = lifetime

class C_child_of(core.Component):
    def __init__(self, parent):
        self.parent = parent

class C_scout(core.Component):
    pass

class C_exit(core.Component):
    def __init__(self, name):
        self.name = name

# No entity should have this component which means the system does not require to iterate through entities
class C_none(core.Component):
    pass

