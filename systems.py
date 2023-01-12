# TODO: use a registered function when component_mask gets updated
import sys

sys.path.insert(1, 'core')
import core
import components as comp
import events as evt
from object_storage import Object_storage
import random as rand
import math

# Needs to be even
INVINC_TIME = 20

# for debugging
event_handler_global = None

class S_tick(core.System):
    component_mask = [None]
    def __init__(self, event_handler):
        global event_handler_global
        super().__init__() 
        event_handler_global = event_handler
        self.event_handler = event_handler 
        self.tot_dt = 0

    def run(self, dt):
        if (self.tot_dt >= 0.05):
            self.event_handler.dispatch_event(evt.Tick_event())
            self.event_handler.dispatch_event(evt.Log_event("ticks: ", self.tot_dt))
            self.tot_dt = 0
        else:
            self.tot_dt += dt

class S_render(core.System):
    component_mask = [comp.C_sprite, comp.C_transform]

    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def run(self, dt):
        self.screen.refresh()
        #core.screen.refresh()
        #self.screen.draw_texture(["###","###"], 0, 0)
        if dt != 0:
                print(1 / dt)
        for entity in self.registered_entities:
            [comp_sprite, comp_trans] = entity.query_components([comp.C_sprite, comp.C_transform])
            self.screen.draw_texture(comp_sprite.texture, comp_trans.x, comp_trans.y)

class S_player(core.System):
    component_mask = [comp.C_player, comp.C_transform]
    KEYMAP = {
        ord('w'): [-1, 0],
        ord('d'): [0, 1],
        ord('s'): [1, 0],
        ord('a'): [0, -1]
    }

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            comp_invinc = entity.query_components([comp.C_invincible])
            comp_blink = entity.query_components([comp.C_blink])
            [comp_tran] = entity.query_components([comp.C_transform])

            has_inv = True
            if len(comp_invinc) == 0:
                has_inv = False
            has_blink = True
            if len(comp_blink) == 0:
                has_blink = False

            self.event_handler.dispatch_event(evt.Log_event("Has invun", has_inv))
            self.event_handler.dispatch_event(evt.Log_event("Has blink", has_blink))
            self.event_handler.dispatch_event(evt.Log_event("Position", f"{comp_tran.x:.2f}" + " " + f"{comp_tran.y:.2f}"))

    # refactor screen_wrapper; don't use event handler
    # move this to the run function
    def on_key_event(self, event: core.Key_event):
        if not event.key in self.KEYMAP:
            return
        for entity in self.registered_entities:
            #print(len(self.registered_entities))
            [comp_trans] = entity.query_components([comp.C_transform])
            # TODO: define speed in Player component
            comp_trans.last_x = comp_trans.x
            comp_trans.last_y = comp_trans.y
            comp_trans.y += self.KEYMAP[event.key][0] * 0.02
            comp_trans.x += self.KEYMAP[event.key][1] * 0.02

class S_ghost(core.System):
    component_mask = [comp.C_ghost, comp.C_transform, comp.C_ai]
    def __init__(self, world):
        super().__init__()
        self.world = world
    
    def run(self, dt):
        for entity in self.registered_entities:
            [comp_ghost, comp_tran, comp_ai] = entity.query_components([comp.C_ghost, comp.C_transform, comp.C_ai])
            if comp_ghost.target == None or comp_ghost.state == comp.C_ghost.STILL:
                continue
            if abs(comp_tran.x - comp_ghost.target[0]) < comp_ghost.speed * dt and abs(comp_tran.y - comp_ghost.target[1]) < comp_ghost.speed * dt:
                comp_ghost.state = comp_ghost.STILL
                comp_ai.disable = 20
                continue
            comp_ai.disable = float("inf")
            comp_tran.last_x = comp_tran.x
            comp_tran.last_y = comp_tran.y
            comp_tran.x += (1 if comp_ghost.target[0] > comp_tran.x else -1) * comp_ghost.speed * dt
            comp_tran.y += (1 if comp_ghost.target[1] > comp_tran.y else -1) * comp_ghost.speed * dt
            # comp_tran.y += comp_ghost.target[1] * comp_ghost.speed * dt

    # TODO: maybe remove _event suffix. The on_ prefix should be enough to specify it to be an even handling function 
    def on_collision_event(self, event):
        entity1_player = event.entity1.query_components([comp.C_player, comp.C_transform])
        entity2_range = event.entity2.query_components([comp.C_range, comp.C_child_of])

        comp_ghost = entity2_range[1].parent.query_components([comp.C_ghost, comp.C_ai])
        if len(comp_ghost) != 2:
            return
        comp_ghost[0].target = [entity1_player[1].x, entity1_player[1].y]
        comp_ghost[0].state = comp_ghost[0].MOVING
        comp_ghost[1].disable = float("inf")

class S_gangster(core.System):
    component_mask = [comp.C_gangster, comp.C_ai, comp.C_transform]

    def __init__(self, event_handler: core.Event_handler, world: core.World):
        super().__init__()
        self.event_handler = event_handler
        self.world = world

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_gang] = entity.query_components([comp.C_gangster])
            self.event_handler.dispatch_event(evt.Log_event("Reload ticks", comp_gang.reload_ticks))

    def on_tick_event(self, event):
        # TODO: make the gangster run away when player is to close
        for entity in self.registered_entities:
            [tran_comp] = entity.query_components([comp.C_transform])
            [comp_ai, comp_gangster] = entity.query_components([comp.C_ai, comp.C_gangster])
            if comp_gangster.state != comp.C_gangster.SHOOTING:
                continue
            if comp_gangster.reload_ticks > 0:
                comp_gangster.reload_ticks -= 1
                continue

            angle = math.atan((comp_gangster.target[1] - tran_comp.y) / (comp_gangster.target[0] - tran_comp.x))
            dir = angle + (0 if comp_gangster.target[0] > tran_comp.x else math.pi)
            Object_storage().clone(self.world, "Projectile", "Bullet", [dir, (tran_comp.x, tran_comp.y)])

            comp_gangster.reload_ticks = 20
            comp_gangster.state = comp.C_gangster.OBSERVING
            comp_ai.disable = 10

    def on_collision_event(self, event: evt.Collision_event):
        [entity1_tran] = event.entity1.query_components([comp.C_transform])
        [entity2_child] = event.entity2.query_components([comp.C_child_of])
        comp_gangster = entity2_child.parent.query_components([comp.C_gangster, comp.C_ai])
        if len(comp_gangster) != 2:
            return
        comp_gangster[0].target = [entity1_tran.x, entity1_tran.y]
        comp_gangster[0].state = comp_gangster[0].SHOOTING
        comp_gangster[1].disable = float("INF")

class S_boomer(core.System):
    component_mask = [comp.C_boomer, comp.C_transform]

    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.world = world
    
    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [comp_boom, comp_tran] = entity.query_components([comp.C_boomer, comp.C_transform])
            if comp_boom.reload_ticks <= 0:
                comp_boom.reload_ticks = comp_boom.fire_rate
                Object_storage().clone(self.world, "Projectile", "Bomb", [(rand.uniform(0.1,0.9), rand.uniform(0.1,0.9)), 0.1, 10]) 
                continue
            comp_boom.reload_ticks -= 1


class S_fox(core.System):
    component_mask = [comp.C_fox, comp.C_transform]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler
    
    def run(self, dt):
        for entity in self.registered_entities: 
            [comp_tran, comp_fox, comp_ai] = entity.query_components([comp.C_transform, comp.C_fox, comp.C_ai])
            if comp_fox.target == None or comp_fox.state != comp.C_fox.DASHING:
                continue

            if abs(comp_tran.x - comp_fox.target[0]) < comp_fox.speed * dt and abs(comp_tran.y - comp_fox.target[1]) < comp_fox.speed * dt:
                comp_ai.disable = 5
                comp_fox.state = comp.C_fox.IDLE
                continue

            angle = math.atan((comp_fox.target[1] - comp_tran.y) / (comp_fox.target[0] - comp_tran.x))
            dir = angle + (0 if comp_fox.target[0] > comp_tran.x else math.pi)
            hor_move = math.cos(dir) * dt * comp_fox.speed
            ver_move = math.sin(dir) * dt * comp_fox.speed
            comp_tran.last_x = comp_tran.x
            comp_tran.last_y = comp_tran.y
            comp_tran.x += hor_move
            comp_tran.y += ver_move


    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [comp_fox, comp_ai] = entity.query_components([comp.C_fox, comp.C_ai])

            match comp_fox.state:
                case comp.C_fox.IDLE:
                    K = 0.06 + comp_fox.sensitivity / 1000
                    threshold = 1 / (1 + pow(math.e, -K * (comp_fox.ticks_since_last_dash - 2000 * K))) 
                    if rand.uniform(0, 1) <= threshold:
                        comp_fox.ticks_since_last_dash = 0
                        if comp_fox.target == None:
                            continue
                        comp_fox.state = comp.C_fox.DASHING
                        comp_ai.disable = float("inf")
                    else:
                        comp_fox.ticks_since_last_dash += 1

    def on_collision_event(self, event: evt.Collision_event):
        [entity1_tran] = event.entity1.query_components([comp.C_transform])
        [entity2_child] = event.entity2.query_components([comp.C_child_of])
        comp_fox = entity2_child.parent.query_components([comp.C_fox, comp.C_ai])
        if len(comp_fox) != 2:
            return
        if comp_fox[0].state == comp.C_fox.DASHING:
            return
        comp_fox[0].target = [entity1_tran.x, entity1_tran.y]


class S_monkey(core.System):
    component_mask = [comp.C_monkey, comp.C_transform]

    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.world = world

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [comp_monk, comp_tran] = entity.query_components([comp.C_monkey, comp.C_transform]) 
            match comp_monk.state:
                # Do nothing; happens when a player hasn't been detected yet and between phases
                case comp.C_monkey.IDLE:
                    continue
                # phase 1: shoot burst of bullets
                case comp.C_monkey.PHASE_1:
                    if comp_monk.phase_state.reload_time > 0:
                        comp_monk.phase_state.reload_time -= 1
                        continue
                    angle = math.atan((comp_monk.target[1] - comp_tran.y) / (comp_monk.target[0] - comp_tran.x))
                    dir = angle + (0 if comp_monk.target[0] > comp_tran.x else math.pi)
                    Object_storage().clone(self.world, "Projectile", "Bullet", [dir, (comp_tran.x, comp_tran.y)])
                    comp_monk.phase_state.reload_time = 500
                case comp.C_monkey.PHASE_2:
                    pass
                case comp.C_monkey.PHASE_3:
                    pass

        # phase 2: throw bombs
        # phase 3: tail player



    def on_collision_event(self, event: evt.Collision_event):
        [entity1_tran] = event.entity1.query_components([comp.C_transform])
        [entity2_child] = event.entity2.query_components([comp.C_child_of])
        comp_monkey = entity2_child.parent.query_components([comp.C_monkey, comp.C_ai])
        if len(comp_monkey) != 2:
            return
        comp_monkey[0].target = [entity1_tran.x, entity1_tran.y]
        comp_monkey[0].state = comp.C_monkey.IDLE
        # comp_monkey[0].phase_state = comp.C_monkey.Phase_1(0)


class S_bomb(core.System):
    component_mask = [comp.C_bomb, comp.C_transform]
    
    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.world = world

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        destroy_lst = []
        for entity in self.registered_entities:
            [comp_tran, comp_bomb] = entity.query_components([comp.C_transform, comp.C_bomb])
            if comp_bomb.det_time <= 0:
                Object_storage().clone(self.world, "Misc", "Explosion", [(comp_tran.x - comp_bomb.radius, comp_tran.y - comp_bomb.radius), comp_bomb.radius])
                destroy_lst.append(entity)
                continue
            comp_bomb.det_time -= 1
        for entity in destroy_lst:
            entity.destroy_entity()


# TODO: create system which destroys the entity and use event to call it, instead of directly call destroy_entity. This because we need to also destroy all the children

class S_range(core.System):
    component_mask = [comp.C_range, comp.C_transform, comp.C_child_of]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_tran, comp_child, comp_range] = entity.query_components([comp.C_transform, comp.C_child_of, comp.C_range])
            [comp_parent] = comp_child.parent.query_components([comp.C_transform])
            comp_tran.last_x = comp_tran.x
            comp_tran.last_y = comp_tran.y
            comp_tran.x = comp_parent.x + comp_range.offset[0]
            comp_tran.y = comp_parent.y + comp_range.offset[1]

class S_bullet(core.System):
    component_mask = [comp.C_bullet, comp.C_transform]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_bull, comp_tran] = entity.query_components([comp.C_bullet, comp.C_transform])
            self.event_handler.dispatch_event(evt.Log_event("Bullet dir", comp_bull.dir * 180 / math.pi))
            hor_move = math.cos(comp_bull.dir) * dt * comp_bull.speed
            ver_move = math.sin(comp_bull.dir) * dt * comp_bull.speed
            comp_tran.last_x = comp_tran.x
            comp_tran.last_y = comp_tran.y
            comp_tran.x += hor_move
            comp_tran.y += ver_move

    def on_collision_event(self, event: evt.Collision_event):
        # Assumes only ONE entity is a bullet
        event.entity1.destroy_entity()

    def on_cleanup_event(self, event: evt.Cleanup_event):
        count = 0
        while len(self.registered_entities) > 0:
            self.registered_entities[0].destroy_entity()    # modifies the registered entities list which means we do not need to manually remove element from the list
            count += 1
        self.event_handler.dispatch_event(evt.Log_event("CLEANED", count))

# Destroys entities who are out of range
class S_void(core.System):
    component_mask = [comp.C_transform, comp.C_sprite]

    def __init__(self, event_handler: core.Event_handler, screen: core.Window):
        super().__init__()
        self.event_handler = event_handler 
        self.screen = screen

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_tran] = entity.query_components([comp.C_transform])
            if comp_tran.x < 0 or comp_tran.x >= 1 or comp_tran.y < 0 or comp_tran.y >= 1:
                entity.destroy_entity()

class S_ai(core.System):
    component_mask = [comp.C_ai, comp.C_transform]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_ai, comp_tran] = entity.query_components([comp.C_ai, comp.C_transform])
            if comp_ai.disable > 0:
                continue
            if comp_ai.target != None:
                self.event_handler.dispatch_event(evt.Log_event("Ai_target: ", f"{comp_ai.target[0]:.2f}, {comp_ai.target[1]:.2f}"))
            if comp_ai.target == None or (abs(comp_ai.target[0] - comp_tran.x) < comp_ai.speed * dt and (comp_ai.target[1] - comp_tran.y) < comp_ai.speed * dt):
                # new_x = rand.uniform(0.2, 0.8)
                # new_y = rand.uniform(0.2, 0.8)
                new_x = rand.uniform(comp_ai.area[0][0], comp_ai.area[1][0])
                new_y = rand.uniform(comp_ai.area[0][1], comp_ai.area[1][1])
                comp_ai.target = (new_x, new_y)
            comp_tran.x += (1 if comp_ai.target[0] > comp_tran.x else -1) * comp_ai.speed * dt
            comp_tran.y += (1 if comp_ai.target[1] > comp_tran.y else -1) * comp_ai.speed * dt

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [comp_ai] = entity.query_components([comp.C_ai])
            comp_ai.disable -= min(comp_ai.disable, 1)  # disable should always be a non negative integer


class S_lifetime(core.System):
    component_mask = [comp.C_lifetime]
    def __init__(self):
        super().__init__()

    # TODO: do this on tick instead of every frame
    def run(self, dt):
        for entity in self.registered_entities:
            [life_comp] = entity.query_components([comp.C_lifetime])
            if life_comp.lifetime == 0:
                entity.destroy_entity()
            life_comp.lifetime -= 1

class S_collision(core.System):
    component_mask = [comp.C_hitbox, comp.C_transform]
    def __init__(self, event_handler, screen):
        super().__init__()
        self.event_handler = event_handler
        self.screen = screen

    def run(self, dt):
        for i,entity1 in enumerate(self.registered_entities):
            for j,entity2 in enumerate(self.registered_entities):
                if j <= i:
                    continue
                # 🤫 TODO: fix, the event might destroy the entity which means stuff breaks. The for loop might also become invalid / skip entities
                try:
                    [hit_comp1, tran_comp1] = entity1.query_components([comp.C_hitbox, comp.C_transform])
                    [hit_comp2, tran_comp2] = entity2.query_components([comp.C_hitbox, comp.C_transform])
                except:
                    continue
                # rel_hit_comp1 = self.screen.abs_to_rel(hit_comp1.w, hit_comp1.h) if not hit_comp1.relative_pos else [hit_comp1.w, hit_comp1.h]
                # rel_hit_comp2 = self.screen.abs_to_rel(hit_comp2.w, hit_comp2.h) if not hit_comp2.relative_pos else [hit_comp2.w, hit_comp2.h]
                rel_hit_comp1 = self.screen.abs_to_rel(hit_comp1.w, hit_comp1.h) if not hit_comp1.relative_pos else [hit_comp1.w, hit_comp1.h]
                rel_hit_comp2 = self.screen.abs_to_rel(hit_comp2.w, hit_comp2.h) if not hit_comp2.relative_pos else [hit_comp2.w, hit_comp2.h]
                if tran_comp1.x < rel_hit_comp2[0] + tran_comp2.x and \
                    tran_comp1.x + rel_hit_comp1[0] > tran_comp2.x and \
                    tran_comp1.y < rel_hit_comp2[1] + tran_comp2.y and \
                    tran_comp1.y + rel_hit_comp1[1] > tran_comp2.y: \
                    self.event_handler.dispatch_event(evt.Collision_event(entity1, entity2))

class S_impenetrable(core.System):
    component_mask = [comp.C_impenetrable, comp.C_transform]
    def __init__(self):
        super().__init__()

    def run(self, dt):
        pass

    def on_collision_event(self, event):
        # Assumes only ONE is impenetrable
        # TODO: make so you go right against the impenetrable object, otherwise there will be a a big gap
        [comp_imp] = event.entity1.query_components([comp.C_impenetrable]) 
        [comp_trans] = event.entity2.query_components([comp.C_transform])
        comp_trans.x = comp_trans.last_x
        comp_trans.y = comp_trans.last_y

class S_blink(core.System):
    component_mask = [comp.C_blink, comp.C_sprite]

    def __init__(self):
        super().__init__()

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [comp_blink, comp_sprite] = entity.query_components([comp.C_blink, comp.C_sprite])
            tmp_text = comp_sprite.texture
            comp_sprite.texture = comp_blink.next_texture
            comp_blink.next_texture = tmp_text

    def on_cleanup_event(self, event: evt.Cleanup_event):
        for entity in self.registered_entities:
            [comp_blink, comp_sprite] = entity.query_components([comp.C_blink, comp.C_sprite])
            if comp_sprite.texture == [""]:
                tmp_text = comp_sprite.texture
                comp_sprite.texture = comp_blink.next_texture
                comp_blink.next_texture = tmp_text

# Does an action after a specified amount of time / ticks
class H_delay():
    def __init__(self):
        self.actions = []

    def on_tick_event(self, event: evt.Tick_event):
        done_lst = []
        for i,(action,delay) in enumerate(self.actions):
            if delay == 0:
                action()
                # swap with the last element instead for better performance
                done_lst.append(i)
                continue
            self.actions[i][1] -= 1
        done_lst.reverse()
        for i in done_lst:
            self.actions.pop(i)

    def on_delay_event(self, event: evt.Delay_event):
        self.actions.append([event.action, event.delay])

    def on_cleanup_event(self, event: evt.Cleanup_event):
        for action,delay in self.actions:
            action()
        self.actions = []

class H_thorn():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_collision_event(self, event: evt.Collision_event):
        # Assumes both entities doesn't have the thorn and health component
        # TODO: call take damage event or something similar and do the checks in the health_system instead
        comp_thorn = event.entity1.query_components([comp.C_thorn])
        comp_health = event.entity2.query_components([comp.C_health])

        comp_player = event.entity2.query_components([comp.C_player])
        if len(comp_player) != 0 and len(comp_health) != 0 and len(event.entity2.query_components([comp.C_invincible])) == 0:
            comp_health[0].health -= comp_thorn[0].damage
            event.entity2.add_component(comp.C_invincible())
            event.entity2.add_component(comp.C_blink())
            # OBS: INVIC_TIME has to be even, otherwise the player will be invisible when blink components get removed
            self.event_handler.dispatch_event(evt.Delay_event(
                lambda: event.entity2.remove_component(comp.C_invincible), INVINC_TIME))
            self.event_handler.dispatch_event(evt.Delay_event(
                lambda: event.entity2.remove_component(comp.C_blink), INVINC_TIME))

class H_enemythorn():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_collision_event(self, event: evt.Collision_event):
        # Assumes both entities doesn't have the enemythorn and health component
        # TODO: call take damage event or something similar and do the checks in the health_system instead
        [comp_enemythorn] = event.entity1.query_components([comp.C_enemythorn])
        [comp_health] = event.entity2.query_components([comp.C_health])

        if len(event.entity2.query_components([comp.C_invincible])) == 0:
            comp_health.health -= comp_enemythorn.damage
            event.entity2.add_component(comp.C_invincible())
            # OBS: INVIC_TIME has to be even, otherwise the monster will be invisible when blink components get removed
            self.event_handler.dispatch_event(evt.Delay_event(
                lambda: event.entity2.remove_component(comp.C_invincible), 10))


class H_exit():
    def __init__(self, exit_lst):
        self.exit_lst = exit_lst

    def on_collision_event(self, event: evt.Collision_event):
        [comp_exit] = event.entity1.query_components([comp.C_exit])
        self.exit_lst.append(comp_exit.name)

class S_debug_render_rectangle(core.System):
    component_mask = [comp.C_rectangle, comp.C_transform]

    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def run(self, dt):
        #self.screen.refresh()
        for entity in self.registered_entities:
            # TODO: don't assume that it uses relative position
            [comp_rectangle, comp_trans] = entity.query_components([comp.C_rectangle, comp.C_transform])
            self.screen.draw_rectangle(comp_trans.x, comp_trans.y, comp_rectangle.width, comp_rectangle.height)

class S_debug_render_text(core.System):
    component_mask = [comp.C_text, comp.C_transform]

    def __init__(self, screen: core.Window):
        super().__init__()
        self.screen = screen

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_text, comp_tran] = entity.query_components([comp.C_text, comp.C_transform])
            self.screen.draw_text(comp_tran.x, comp_tran.y, comp_text.text)
            self.screen.refresh()

class S_debug_player(core.System):
    component_mask = [comp.C_health, comp.C_player]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_health] = entity.query_components([comp.C_health])
            self.event_handler.dispatch_event(evt.Log_event("Player_health: ", comp_health.health))

class H_debug_keypress():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler
    
    def on_key_event(self, event: core.Key_event):
        if event.key == ord('f'):
            self.event_handler.dispatch_event(evt.Cleanup_event())

class S_logging(core.System):
    component_mask = [comp.C_none]

    def __init__(self, screen: core.Window):
        super().__init__()
        self.screen = screen
        self.d = {}

    def on_log_event(self, event: evt.Log_event):
        self.d[event.key] = event.value

    def run(self, dt):
        i = 0
        for key, value in self.d.items():
            self.screen.draw_text(0, i, str(key) + ": " + str(value))
            i += 0.05
        self.screen.refresh()
