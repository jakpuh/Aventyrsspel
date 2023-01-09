'''
Every entity has one or more of the following "Components"
A component is a attribute which defines a specific quality of an entity
The systems will then iterate through the components of an entity and create behavior
'''
import sys

sys.path.insert(1, 'core')
import core

class C_player(core.Component):
    pass

class C_ghost(core.Component):
    STILL = 0
    MOVING = 1

    # TODO: look more into how python represent enums
    def __init__(self, speed):
        self.speed = speed
        self.target = None
        self.state = self.STILL

class C_gangster(core.Component):
    SHOOTING = 0
    OBSERVING = 1

    def __init__(self, fire_rate, reload_ticks = 10):
        self.fire_rate = fire_rate
        self.state = self.OBSERVING
        self.reload_ticks = reload_ticks     # How many ticks this component should wait until it can shoot
        self.disable = 0

class C_ai(core.Component):
    def __init__(self, speed, area = ((0.2, 0.2), (0.8, 0.8))):
        self.speed = speed
        self.area = area
        self.target = None
        self.disable = 0    # How many ticks this component should be disabled

class C_monkey(core.Component):
    PHASE_1 = 0
    PHASE_2 = 1
    PHASE_3 = 2
    IDLE = 3

    def __init__(self):
        self.state = C_monkey.PHASE_1

class C_bullet(core.Component):
    def __init__(self, dir, speed):    # dir is a angle in radians
        self.dir = dir
        self.speed = speed

class C_thorn():
    def __init__(self, damage):
        self.damage = damage

class C_impenetrable():
    pass

class C_invincible():
    pass

class C_transform(core.Component):
    def __init__(self, x, y):
        # used to revert position when colliding with a wall
        self.last_x = x 
        self.last_y = y
        self.x = x
        self.y = y

class C_sprite(core.Component):
    def __init__(self, texture):
        self.texture = texture

class C_hitbox(core.Component):
    def __init__(self, w, h, relative_pos=False):
        self.w = w
        self.h = h
        self.relative_pos = relative_pos

class C_health(core.Component):
    def __init__(self, health):
        self.health = health  

class C_move(core.Component):
    def __init__(self, speed, dir):
        self.speed = speed
        self.dir = dir

class C_lifetime(core.Component):
    def __init__(self, lifetime):
        self.lifetime = lifetime

class C_blink(core.Component):
    def __init__(self):
        self.next_texture = [""]

class C_child_of(core.Component):
    def __init__(self, parent):
        self.parent = parent

class C_range(core.Component):
    def __init__(self, offset):
        self.offset = offset

class C_exit(core.Component):
    def __init__(self, name):
        self.name = name

# No entity should have this component which means the system does not require to iterate through entities
class C_none(core.Component):
    pass

# ================== DEBUG COMPONENTS (not actually used in the game)======================
class C_rectangle(core.Component):
    def __init__(self, width, height):
        self.width = width
        self.height = height

class C_text(core.Component):
    def __init__(self, text: str):
        self.text = text