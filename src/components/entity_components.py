import core.core as core

class C_transform(core.Component):
    def __init__(self, x, y):
        # used to revert position when colliding with a wall
        self.last_x = x 
        self.last_y = y
        self.x = x
        self.y = y

class C_chest(core.Component):
    def __init__(self, health, damage, speed):
        self.health = health
        self.damage = damage
        self.speed = speed
    pass

class C_dash(core.Component):
    def __init__(self, speed = 0.2, recovery_time = 10):
        self.speed = speed
        self.recovery_time = recovery_time
        
class C_shoot(core.Component):
    def __init__(self, fire_rate, burst_size):
        self.fire_rate = fire_rate
        self.burst_size = burst_size
        self.current_burst_shot = 1
        self.BURST_TICKS = 0    # ticks between each shot in the burst fire

# Makes the entity hurtful to friends but not enemies
class C_enemy(core.Component):
    pass

# Makes the entity hurtful to enemies but not friends
class C_friend(core.Component):
    pass

class C_player(core.Component):
    ATTACK_COOLDOWN = 13

    def __init__(self, speed, damage = 10):
        self.attack_cooldown = 0
        self.speed = speed
        self.damage = damage

class C_ghost(core.Component):
    def __init__(self, speed):
        self.speed = speed

class C_gangster(core.Component):
    pass

class C_throw_bombs(core.Component):
    def __init__(self, fire_rate):
        self.fire_rate = fire_rate

class C_dasher(core.Component):
    def __init__(self):
        self.trigger_type = None

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

    def __init__(self):
        self.phase_state = None

class C_bullet(core.Component):
    def __init__(self, dir, speed):    # dir is a angle in radians
        self.dir = dir
        self.speed = speed

class C_bomb(core.Component):
    def __init__(self, radius, det_time):
        self.radius = radius
        self.det_time = det_time

class C_hitbox(core.Component):
    def __init__(self, w, h, relative_pos=False):
        self.w = w
        self.h = h
        self.relative_pos = relative_pos

class C_move(core.Component):
    def __init__(self, speed, dir):
        self.speed = speed
        self.dir = dir

class C_follow(core.Component):
    def __init__(self, offset, relative_pos = False):
        self.offset = offset
        self.relative_pos = relative_pos