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
    def __init__(self, speed):
        self.speed = speed

class C_thorn():
    def __init__(self, damage):
        self.damage = damage

class C_impenetrable():
    pass

class C_transform(core.Component):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class C_sprite(core.Component):
    def __init__(self, texture):
        self.texture = texture

class C_hitbox(core.Component):
    def __init__(self, w, h):
        self.w = w
        self.h = h

class C_health(core.Component):
    def __init__(self, health):
        self.health = health  

class C_move(core.Component):
    def __init__(self, speed, dir):
        self.speed = speed
        self.dir = dir