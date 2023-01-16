'''
Every entity has one or more of the following "Components"
A component is a attribute which defines a specific quality of an entity
The systems will then iterate through the components of an entity and create behavior
'''
import core.core as core

class C_shoot(core.Component):
    def __init__(self, fire_rate, burst_size):
        self.fire_rate = fire_rate
        self.burst_size = burst_size
        self.current_burst_shot = 1
        self.BURST_TICKS = 0    # ticks between each shot in the burst fire

class C_target(core.Component):
    def __init__(self, target):
        self.target = target

# Makes the entity hurtful to friends but not enemies
class C_enemy(core.Component):
    pass

# Makes the entity hurtful to enemies but not friends
class C_friend(core.Component):
    pass

# Makes the entity hurtful to everything
class C_joker(core.Component):
    pass

class C_xp(core.Component):
    def __init__(self, xp):
        self.xp = xp

class C_boss_game_manager(core.Component):
    def __init__(self, action):
        self.action = action

class C_player(core.Component):
    ATTACK_COOLDOWN = 13

    def __init__(self):
        self.attack_cooldown = 0

class C_ghost(core.Component):
    def __init__(self, speed):
        self.speed = speed

class C_gangster(core.Component):
    pass

class C_boomer(core.Component):
    def __init__(self, fire_rate):
        self.fire_rate = fire_rate
        self.reload_ticks = fire_rate

class C_throw_bombs(core.Component):
    def __init__(self, fire_rate):
        self.fire_rate = fire_rate

class C_fox(core.Component):
    IDLE = 0
    DASHING = 1

    def __init__(self, sensitivity = 0):
        self.target = None
        self.state = self.IDLE
        self.sensitivity = sensitivity  
        self.ticks_since_last_dash = 0
        self.speed = 0.2
    
class C_delay(core.Component):
    def __init__(self, actions: list[tuple[2]] = [], named_actions: dict = {}):
        self.named_actions = named_actions
        self.actions = actions

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

    class Phase_1():
        def __init__(self, reload_time):
            self.reload_time = reload_time
    
    class Phase_2():
        def __init__(self, fire_rate):
            self.fire_rate = fire_rate
            self.reload_ticks = fire_rate


    class Phase_3():
        pass

    def __init__(self):
        self.state = C_monkey.IDLE
        self.target = None
        self.phase_state = None

class C_bullet(core.Component):
    def __init__(self, dir, speed):    # dir is a angle in radians
        self.dir = dir
        self.speed = speed

class C_thorn():
    def __init__(self, damage):
        self.damage = damage

class C_enemythorn():
    def __init__(self, damage):
        self.damage = damage

class C_monster():
    pass

class C_bomb(core.Component):
    def __init__(self, radius, det_time):
        self.radius = radius
        self.det_time = det_time

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

class C_animation(core.Component):
    def __init__(self, textures: list, animation_speed = 0):
        self.textures = textures
        self.animation_speed = animation_speed
        self.index = 0
        self.remaining_ticks = 0

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

class C_scout(core.Component):
    pass

class C_exit(core.Component):
    def __init__(self, name):
        self.name = name

class C_follow(core.Component):
    def __init__(self, offset, relative_pos = False):
        self.offset = offset
        self.relative_pos = relative_pos

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