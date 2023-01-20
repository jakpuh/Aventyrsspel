import core.core as core

class C_invincible():
    pass

class C_sprite(core.Component):
    def __init__(self, texture):
        self.texture = texture

class C_animation(core.Component):
    def __init__(self, textures: list, animation_speed = 0):
        self.textures = textures
        self.animation_speed = animation_speed
        self.index = 0
        self.remaining_ticks = 0

class C_blink(core.Component):
    def __init__(self):
        self.next_texture = [""]

class C_rectangle(core.Component):
    def __init__(self, width, height):
        self.width = width
        self.height = height

# ==== DEBGUG ====
class C_text(core.Component):
    def __init__(self, text: str):
        self.text = text