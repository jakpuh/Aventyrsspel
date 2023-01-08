'''
Small snake game clone to check that the core components work
'''
import sys

sys.path.insert(1, 'core')
import core
import time
import random as rand

class Move_event(core.Event):
    def __init__(self, entity):
        self.entity = entity

class Collision_event(core.Event):
    def __init__(self, entities):
        self.entities = entities 

class C_sprite(core.Component):
    def __init__(self, texture):
        self.texture = texture

class C_transform(core.Component):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
class C_player(core.Component):
    def __init__(self, velocity, dir, len):
        self.velocity = velocity
        self.dir = dir
        self.base_dir = dir
        self.len = len

class C_lifetime(core.Component):
    def __init__(self, time_alive):
        self.time_alive = time_alive

class C_apple(core.Component):
    pass

class S_render(core.System):
    def __init__(self):
        super().__init__()
        self.component_mask = [C_transform, C_sprite]

    def run(self, dt):
        if dt != 0:
            core.Screen_wrapper().draw_texture([str(1/dt)], 0, 0)
        for entity in self.registered_entities:
            [tran_comp, sprite_comp] = entity.query_components([C_transform, C_sprite])
            core.Screen_wrapper().draw_texture(sprite_comp.texture, tran_comp.x, tran_comp.y)

class S_player(core.System):
    def __init__(self, event_handler):
        super().__init__()
        self.component_mask = [C_transform, C_player]
        self.event_handler = event_handler
        self.len = 1

    def run(self, dt):
        [height, width] = core.Screen_wrapper().get_dimension()
        for entity in self.registered_entities:
            [tran_comp, player_comp] = entity.query_components([C_transform, C_player])
            next_pos_x = tran_comp.x + player_comp.dir[0] * player_comp.velocity * (height / width) * dt
            next_pos_y = tran_comp.y + player_comp.dir[1] * player_comp.velocity * dt
            if int(next_pos_x * width) != int(tran_comp.x * width) or int(next_pos_y * height) != int(tran_comp.y * height):
                tail = self.world.create_entity()
                tail.add_component(C_lifetime(0))
                tail.add_component(C_sprite("."))
                tail.add_component(C_transform(tran_comp.x, tran_comp.y))
                self.event_handler.dispatch_event(Move_event(entity))
                self.len += 1
            tran_comp.x = next_pos_x
            tran_comp.y = next_pos_y

    def on_keypress(self, event):
        for entity in self.registered_entities:
            [move_comp] = entity.query_components([C_player])
            if event.key == ord('w') and move_comp.base_dir != [0, 1]:
                move_comp.dir = [0, -1]
            elif event.key == ord('d') and move_comp.base_dir != [-1, 0]:
                move_comp.dir = [1, 0]
            elif event.key == ord('s') and move_comp.base_dir != [0, -1]:
                move_comp.dir = [0, 1]
            elif event.key == ord('a') and move_comp.base_dir != [1, 0]:
                move_comp.dir = [-1, 0]

    def on_collision(self, event):
        player_entities = []
        apple_count = 0
        for entity in event.entities:
            player_comp = entity.query_components([C_player, C_transform])
            apple_comp = entity.query_components([C_apple, C_transform])
            if len(player_comp) == 2:
                player_entities.append(player_comp[1])
            elif len(apple_comp) == 2:
                apple_count += 1
        for player in player_entities:
            for _ in range(apple_count):
                tail = self.world.create_entity()
                tail.add_component(C_lifetime(0))
                tail.add_component(C_sprite("."))
                tail.add_component(C_transform(player.x, player.y))

    def on_move(self, event):
        player_comp_lst = event.entity.query_components([C_player])
        if player_comp_lst != []:
            player_comp_lst[0].base_dir = player_comp_lst[0].dir

class S_lifetime(core.System):
    def __init__(self):
        super().__init__()
        self.component_mask = [C_lifetime]

    def run(self, dt):
        for entity in self.registered_entities:
            [life_comp] = entity.query_components([C_lifetime])
            life_comp.time_alive += 1
        
    def on_move(self, event):
        max_time = -1
        max_entity = None
        for entity in self.registered_entities:
            [life_comp] = entity.query_components([C_lifetime])
            if life_comp.time_alive > max_time:
                max_time = life_comp.time_alive
                max_entity = entity
        if max_entity == None:
            return
        max_entity.destroy_entity()

class S_collision(core.System):
    def __init__(self, event_handler):
        super().__init__()
        self.event_handler = event_handler
        self.component_mask = [C_transform]

    # slow, listen on one_move event instead
    def run(self, dt):
        new_events = []
        for i in range(len(self.registered_entities)):
            entity1 = self.registered_entities[i]
            event = [entity1]
            for j in range(i + 1, len(self.registered_entities)):
                entity2 = self.registered_entities[j]
                [tran_comp1] = entity1.query_components([C_transform])
                [tran_comp2] = entity2.query_components([C_transform])
                pixel1 = core.Screen_wrapper().rel_to_abs(tran_comp1.x, tran_comp1.y)
                pixel2 = core.Screen_wrapper().rel_to_abs(tran_comp2.x, tran_comp2.y)
                if pixel1[0] == pixel2[0] and pixel1[1] == pixel2[1]:
                    event.append(entity2)
            if len(event) > 1:
                new_events.append(Collision_event(event))
        for event in new_events:
            self.event_handler.dispatch_event(event)

class Apple_handler():
    def __init__(self, event_system, world):
        self.event_system = event_system
        self.world = world

    def on_collision(self, event):
        for entity in event.entities:
            apple_comp = entity.query_components([C_apple])
            if apple_comp != []:
                entity.destroy_entity()
                new_entity = self.world.create_entity()
                new_entity.add_component(C_transform(rand.uniform(0, 1), rand.uniform(0, 1)))
                new_entity.add_component(C_sprite("🍎"))
                new_entity.add_component(C_apple())

core.Screen_wrapper().init()
event_system = core.Event_handler()

ecs = core.World()
render_system = ecs.add_system(S_render())
player_system = ecs.add_system(S_player(event_system))
lifetime_system = ecs.add_system(S_lifetime())
collision_system = ecs.add_system(S_collision(event_system))
apple_handler = Apple_handler(event_system, ecs)

player_entity = ecs.create_entity()
player_entity.add_component(C_transform(0.5, 0.5))
player_entity.add_component(C_sprite(["🙁"]))
player_entity.add_component(C_player(0.5, [1, 0], 1))

apple_entity = ecs.create_entity()
apple_entity.add_component(C_transform(1, 1))
apple_entity.add_component(C_sprite("$"))
apple_entity.add_component(C_apple())

event_system.subscribe_event(core.Key_event(None), player_system.on_keypress)
event_system.subscribe_event(Move_event(None), lifetime_system.on_move)
event_system.subscribe_event(Collision_event(None), player_system.on_collision)
event_system.subscribe_event(Collision_event(None), apple_handler.on_collision)
event_system.subscribe_event(Move_event(None), player_system.on_move)

dt = 0
while True:
    start = time.time()
    core.Screen_wrapper().poll_events(event_system)
    core.Screen_wrapper().refresh()
    ecs.run(dt)

    stop = time.time()
    dt = stop - start
    time.sleep(max(1 / 60 - dt,0))
    dt = max(dt, 1 / 60)

core.Screen_wrapper().exit()
