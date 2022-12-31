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

class C_thorn():
    def __init__(self, damage):
        self.damage = damage

class C_impenetrable():
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

class C_child_of(core.Component):
    def __init__(self, parent):
        self.parent = parent

class C_range(core.Component):
    pass

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