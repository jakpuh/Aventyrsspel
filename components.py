
import sys

sys.path.insert(1, 'core')
import core

class C_player(core.Component):
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
