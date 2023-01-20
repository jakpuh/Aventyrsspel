# TODO: use a registered function when component_mask gets updated
import core.core as core
import components as comp
import events as evt
from object_storage import Object_storage
import random as rand
import math

class H_scout():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_collision_event(self, event: evt.Collision_event):
        self.event_handler.dispatch_event(evt.Log_event("scout", rand.uniform(-1, 1)))
        [comp_child] = event.entity1.query_components([comp.C_child_of])
        [comp_tran] = event.entity2.query_components([comp.C_transform])
        if (len(comp_child.parent.query_components([comp.C_target])) == 0):
            self.event_handler.dispatch_event(evt.Add_component_event(comp.C_target, comp_child.parent))
        comp_child.parent.add_component(comp.C_target((comp_tran.x, comp_tran.y)))
        self.event_handler.dispatch_event(evt.Target_event(comp_child.parent))

class S_xp(core.System):
    component_mask = [comp.C_xp]

class S_gm_boss(core.System):
    component_mask = [comp.C_boss_game_manager]
    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler
    
    def run(self, dt):
        pass

    def on_destroy_entity_event(self, event: evt.Destroy_entity_event):
        if len(event.entity.query_components([comp.C_monkey])) == 0:
            return
        for entity in self.registered_entities:
            [comp_gm_boss] = entity.query_components([comp.C_boss_game_manager])
            comp_gm_boss.action() 

class S_tick(core.System):
    component_mask = [None]
    def __init__(self, event_handler):
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
            if comp_sprite.texture == None:
                continue
            try:
                self.screen.draw_texture(comp_sprite.texture, comp_trans.x, comp_trans.y)
            except:
                pass

class S_player(core.System):
    component_mask = [comp.C_player, comp.C_transform]

    KEYMAP = {
        ord('w'): [-1, 0],
        ord('d'): [0, 1],
        ord('s'): [1, 0],
        ord('a'): [0, -1],
    }

    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.world = world


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

    def on_tick_event(self, event):
        for entity in self.registered_entities:
            [comp_player]  = entity.query_components([comp.C_player])
            comp_player.attack_cooldown = max(comp_player.attack_cooldown - 1, 0)

    def _attack(self):
        for entity in self.registered_entities:
            [comp_player] = entity.query_components([comp.C_player])
            if comp_player.attack_cooldown > 0:
                continue
            Object_storage().clone(self.world, "Misc", "Spinning-swords", [entity])
            comp_player.attack_cooldown = comp.C_player.ATTACK_COOLDOWN

    # refactor screen_wrapper; don't use event handler
    # move this to the run function
    def on_key_event(self, event: core.Key_event):
        if event.key == ord(' '):
            self._attack()
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
    component_mask = [comp.C_ghost, comp.C_transform, comp.C_target]
    def __init__(self, world):
        super().__init__()
        self.world = world
    
    def run(self, dt):
        for entity in self.registered_entities:
            [comp_ghost, comp_tran, comp_target] = entity.query_components([comp.C_ghost, comp.C_transform, comp.C_target])
            if abs(comp_tran.x - comp_target.target[0]) < comp_ghost.speed * dt and abs(comp_tran.y - comp_target.target[1]) < comp_ghost.speed * dt:
                comp_delay = entity.query_components([comp.C_delay])
                actions = {
                    "Remove-target": (lambda entity: entity.remove_component(comp.C_target), 20),
                    "Add-ai": (lambda entity: entity.add_component(comp.C_ai(0.06)), 20)
                }
                for key,value in actions.items():
                    if key not in comp_delay[0].named_actions:
                        comp_delay[0].named_actions[key] = value
                continue
                
            comp_tran.last_x = comp_tran.x
            comp_tran.last_y = comp_tran.y
            comp_tran.x += (1 if comp_target.target[0] > comp_tran.x else -1) * comp_ghost.speed * dt
            comp_tran.y += (1 if comp_target.target[1] > comp_tran.y else -1) * comp_ghost.speed * dt

    def on_target_event(self, event: evt.Target_event):
        comp_ghost = event.entity.query_components([comp.C_ghost])
        if len(comp_ghost) == 0:
            return
        event.entity.remove_component(comp.C_ai) 

class S_gangster(core.System):
    component_mask = []

    def __init__(self, event_handler: core.Event_handler, world: core.World):
        super().__init__()

    def run(self, dt):
        pass

class S_shoot(core.System):
    component_mask = [comp.C_shoot, comp.C_transform, comp.C_target]

    def __init__(self, event_handler: core.Event_handler, world: core.World):
        super().__init__()
        self.event_handler = event_handler
        self.world = world

    def _delay_next_shoot(self, entity, delay):
        [comp_shoot] = entity.query_components([comp.C_shoot])
        [comp_delay] = entity.query_components([comp.C_delay])
        actions = {
            "Add-shoot": (lambda entity: entity.add_component(comp_shoot), delay)
        }
        entity.remove_component(comp.C_shoot)
        for key,action in actions.items():
            if key not in comp_delay.named_actions:
                comp_delay.named_actions[key] = action

    def run(self, dt):
        pass

    def on_tick_event(self, dt):
        # TODO: make the gangster run away when player is to close
        for entity in self.registered_entities:
            [comp_target, comp_tran, comp_shoot] = entity.query_components([comp.C_target, comp.C_transform, comp.C_shoot])
            angle = math.atan((comp_target.target[1] - comp_tran.y) / (comp_target.target[0] - comp_tran.x))
            dir = angle + (0 if comp_target.target[0] > comp_tran.x else math.pi)
            Object_storage().clone(self.world, "Projectile", "Bullet", [dir, (comp_tran.x, comp_tran.y)])

            if comp_shoot.current_burst_shot == comp_shoot.burst_size:
                next_shot_delay = comp_shoot.fire_rate
                comp_shoot.current_burst_shot = 1
            else:
                next_shot_delay = comp_shoot.BURST_TICKS
                comp_shoot.current_burst_shot += 1

            self._delay_next_shoot(entity, next_shot_delay)

    def on_target_event(self, event: evt.Target_event):
        comp_gangster = event.entity.query_components([comp.C_gangster])
        if len(comp_gangster) == 0:
            return

        [comp_delay] = event.entity.query_components([comp.C_delay])
        actions = {
            "Remove-target": (lambda entity: entity.remove_component(comp.C_target), 30),
            "Add-ai": (lambda entity: entity.add_component(comp.C_ai(0.01)), 30)
        }
        comp_delay.named_actions.update(actions)
    
    def on_add_component_event(self, event: evt.Add_component_event):
        comp_shoot = event.entity.query_components([comp.C_shoot])
        if len(comp_shoot) == 0:
            return
        if (event.component_type != comp.C_target):
            return

        event.entity.remove_component(comp.C_ai) 
        self._delay_next_shoot(event.entity, comp_shoot[0].fire_rate)

class S_boomer(core.System):
    component_mask = [comp.C_boomer, comp.C_transform]

    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.world = world
    
    def run(self, dt):
        pass

class S_throw_bombs(core.System):
    component_mask = [comp.C_throw_bombs, comp.C_transform]

    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.world = world
    
    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            Object_storage().clone(self.world, "Projectile", "Bomb", [(rand.uniform(0.1,0.9), rand.uniform(0.1,0.9)), 0.1, 10]) 

            [comp_delay, comp_throw_bombs] = entity.query_components([comp.C_delay, comp.C_throw_bombs])
            actions = {
                "Add-throw_bombs": (lambda entity: entity.add_component(comp_throw_bombs), comp_throw_bombs.fire_rate)
            }
            comp_delay.named_actions.update(actions)
            entity.remove_component(comp.C_throw_bombs)

class H_fox():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler
    
    def on_trigger_event(self, event: evt.Trigger_event):
        comps = event.entity.query_components([comp.C_fox, comp.C_target])
        if len(comps) != 2:
            return

        event.entity.disable_group([event.trigger_type, comp.C_ai], "AI")
        [comp_delay] = event.entity.query_components([comp.C_delay])
        comp_delay.actions.append((lambda entity: entity.add_component(comp.C_dash(0.3)), 10))
    
    def on_finish_event(self, event: evt.Finished_event):
        comps = event.entity.query_components([comp.C_fox])
        if len(comps) == 0 or event.component != comp.C_dash:
            return
        
        event.entity.remove_component(comp.C_dash)
        [comp_delay] = event.entity.query_components([comp.C_delay])
        comp_delay.actions.append((lambda entity: entity.enable_group("AI"), 10))

class S_dash(core.System):
    component_mask = [comp.C_dash, comp.C_transform, comp.C_target]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_dash, comp_tran, comp_target] = entity.query_components([comp.C_dash, comp.C_transform, comp.C_target])
            if abs(comp_tran.x - comp_target.target[0]) < comp_dash.speed * dt and abs(comp_tran.y - comp_target.target[1]) < comp_dash.speed * dt:
                self.event_handler.dispatch_event(evt.Finished_event(entity, comp.C_dash))
                return

            angle = math.atan((comp_target.target[1] - comp_tran.y) / (comp_target.target[0] - comp_tran.x))
            dir = angle + (0 if comp_target.target[0] > comp_tran.x else math.pi)
            hor_move = math.cos(dir) * dt * comp_dash.speed
            ver_move = math.sin(dir) * dt * comp_dash.speed
            comp_tran.last_x = comp_tran.x
            comp_tran.last_y = comp_tran.y
            comp_tran.x += hor_move
            comp_tran.y += ver_move

class S_normal_trigger(core.System):
    component_mask = [comp.C_normal_trigger]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [comp_trig] = entity.query_components([comp.C_normal_trigger])
            K = 0.06 + comp_trig.sensitivity / 1000
            threshold = 1 / (1 + pow(math.e, -K * (comp_trig.ticks_since_last_trigger - 2000 * K))) 
            if rand.uniform(0, 1) <= threshold:
                comp_trig.ticks_since_last_trigger = 0
                self.event_handler.dispatch_event(evt.Trigger_event(entity, comp.C_normal_trigger))
            else:
                comp_trig.ticks_since_last_trigger += 1

class S_monkey(core.System):
    component_mask = [comp.C_monkey, comp.C_transform, comp.C_fox, comp.C_boomer]

    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.world = world

    def run(self, dt):
        for entity in self.registered_entities: 
            return
            [comp_tran, comp_fox, comp_ai] = entity.query_components([comp.C_transform, comp.C_fox, comp.C_ai])
            if comp_fox.target == None or comp_fox.state != comp.C_fox.DASHING:
                continue

            if abs(comp_tran.x - comp_fox.target[0]) < comp_fox.speed * dt and abs(comp_tran.y - comp_fox.target[1]) < comp_fox.speed * dt:
                comp_ai.disable = 5
                comp_fox.state = comp.C_fox.IDLE
                comp_fox.target = None
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
            continue
            [comp_monk, comp_tran, comp_boom, comp_fox, comp_ai] = entity.query_components([comp.C_monkey, comp.C_transform, comp.C_boomer, comp.C_fox, comp.C_ai]) 
            match 0:
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
                    if comp_boom.reload_ticks <= 0:
                        comp_boom.reload_ticks = comp_boom.fire_rate
                        Object_storage().clone(self.world, "Projectile", "Bomb", [(rand.uniform(0.1,0.9), rand.uniform(0.1,0.9)), 0.1, 10]) 
                        continue
                    comp_boom.reload_ticks -= 1
                case comp.C_monkey.PHASE_3:
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
        for entity in self.registered_entities:
            [comp_tran, comp_bomb] = entity.query_components([comp.C_transform, comp.C_bomb])
            if comp_bomb.det_time <= 0:
                Object_storage().clone(self.world, "Misc", "Explosion", [(comp_tran.x - comp_bomb.radius, comp_tran.y - comp_bomb.radius), comp_bomb.radius])
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))
                continue
            comp_bomb.det_time -= 1

# TODO: create system which destroys the entity and use event to call it, instead of directly call destroy_entity. This because we need to also destroy all the children

class S_follow(core.System):
    component_mask = [comp.C_follow, comp.C_transform, comp.C_child_of]

    def __init__(self, event_handler: core.Event_handler, screen):
        super().__init__()
        self.event_handler = event_handler
        self.screen = screen

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_tran, comp_child, comp_follow] = entity.query_components([comp.C_transform, comp.C_child_of, comp.C_follow])
            [comp_parent] = comp_child.parent.query_components([comp.C_transform])
            comp_tran.last_x = comp_tran.x
            comp_tran.last_y = comp_tran.y
            rel_offset = self.screen.abs_to_rel(comp_follow.offset[0], comp_follow.offset[1]) if not comp_follow.relative_pos else comp_follow.offset
            comp_tran.x = comp_parent.x + rel_offset[0]
            comp_tran.y = comp_parent.y + rel_offset[1]
            if comp_tran.last_x == None:
                comp_tran.last_x = comp_parent.x + rel_offset[0]
            if comp_tran.last_y == None:
                comp_tran.last_y = comp_parent.y + rel_offset[1]

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
        self.event_handler.dispatch_event(evt.Destroy_entity_event(event.entity1))

    def on_cleanup_event(self, event: evt.Cleanup_event):
        count = 0
        for entity in self.registered_entities:
            self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))
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
            if len(entity.query_components([comp.C_animation])) == 1:
                return
            if comp_tran.x < 0 or comp_tran.x >= 1 or comp_tran.y < 0 or comp_tran.y >= 1:
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))

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
    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        pass

    # TODO: do this on tick instead of every frame
    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [life_comp] = entity.query_components([comp.C_lifetime])
            if life_comp.lifetime == 0:
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))
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
                [hit_comp1, tran_comp1] = entity1.query_components([comp.C_hitbox, comp.C_transform])
                [hit_comp2, tran_comp2] = entity2.query_components([comp.C_hitbox, comp.C_transform])
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
    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        pass

    def on_collision_event(self, event):
        # Assumes only ONE is impenetrable
        # TODO: make so you go right against the impenetrable object, otherwise there will be a a big gap
        # TODO: fix monkey going into wall
        if len(event.entity2.query_components([comp.C_scout, comp.C_animation])) != 0:
            return
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

class S_death(core.System):
    component_mask = [comp.C_health]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_health] = entity.query_components([comp.C_health])
            if comp_health.health <= 0:
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))

class S_animation(core.System):
    component_mask = [comp.C_animation, comp.C_sprite]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [comp_anim, comp_sprite] = entity.query_components([comp.C_animation, comp.C_sprite])
            if comp_anim.remaining_ticks > 0:
                comp_anim.remaining_ticks -= 1
                continue
            if comp_anim.index >= len(comp_anim.textures):
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))
                continue
            comp_sprite.texture = comp_anim.textures[comp_anim.index]
            comp_anim.index += 1
            comp_anim.remaining_ticks = comp_anim.animation_speed

class S_delay(core.System):
    component_mask = [comp.C_delay]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        # TODO: use a muli set in the delay component which sorts by tick
        for entity in self.registered_entities: 
            [comp_delay] = entity.query_components([comp.C_delay])
            remaining_actions = []
            for (action,remaining_ticks) in comp_delay.actions:
                if remaining_ticks <= 0:
                    action(entity)
                    continue
                remaining_actions.append((action, remaining_ticks - 1))
            comp_delay.actions = remaining_actions
            remaining_named_actions = {}
            for name,(action,remaining_ticks) in comp_delay.named_actions.items():
                if remaining_ticks <= 0:
                    action(entity)
                    continue
                remaining_named_actions[name] = (action,remaining_ticks - 1)
            comp_delay.named_actions = remaining_named_actions
    
    def on_cleanup_event(self, event: evt.Cleanup_event):
        for entity in self.registered_entities: 
            [comp_delay] = entity.query_components([comp.C_delay])
            for (action,_) in comp_delay.actions:
                action(entity)
            comp_delay.actions = []

class H_thorn():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_collision_event(self, event: evt.Collision_event):
        # Needs to be odd
        INVINC_TIME = 21

        # Assumes both entities doesn't have the thorn and health component
        # TODO: call take damage event or something similar and do the checks in the health_system instead
        [comp_thorn] = event.entity1.query_components([comp.C_thorn])
        [comp_health] = event.entity2.query_components([comp.C_health])

        comp_player = event.entity2.query_components([comp.C_player])
        if len(comp_player) != 0 and len(event.entity2.query_components([comp.C_invincible])) == 0:
            comp_health.health -= comp_thorn.damage
            event.entity2.add_component(comp.C_invincible())
            event.entity2.add_component(comp.C_blink())
            # OBS: INVIC_TIME has to be even, otherwise the player will be invisible when blink components get removed

            remove_actions = [(lambda entity: entity.remove_component(comp.C_invincible), INVINC_TIME),
                              (lambda entity: entity.remove_component(comp.C_blink), INVINC_TIME)]
            self.event_handler.dispatch_event(evt.Log_event("RANDOM", rand.uniform(-1, 1)))
            comp_delay = event.entity2.query_components([comp.C_delay])
            if len(comp_delay) == 0:
                event.entity2.add_component(comp.C_delay(remove_actions))
            else:
                comp_delay[0].actions.extend(remove_actions)

class H_enemythorn():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_collision_event(self, event: evt.Collision_event):
        INVINC_TIME = 11

        # Assumes both entities doesn't have the enemythorn and health component
        # TODO: call take damage event or something similar and do the checks in the health_system instead
        [comp_enemythorn] = event.entity1.query_components([comp.C_enemythorn])
        [comp_health] = event.entity2.query_components([comp.C_health])

        if len(event.entity2.query_components([comp.C_invincible, comp.C_player])) == 0:
            comp_health.health -= comp_enemythorn.damage
            event.entity2.add_component(comp.C_invincible())
            event.entity2.add_component(comp.C_blink())

            remove_actions = [(lambda entity: entity.remove_component(comp.C_invincible), INVINC_TIME),
                              (lambda entity: entity.remove_component(comp.C_blink), INVINC_TIME)]
            comp_delay = event.entity2.query_components([comp.C_delay])
            if len(comp_delay) == 0:
                event.entity2.add_component(comp.C_delay(remove_actions))
            else:
                comp_delay[0].actions.extend(remove_actions)

class H_exit():
    def __init__(self, exit_lst):
        self.exit_lst = exit_lst

    def on_collision_event(self, event: evt.Collision_event):
        [comp_exit] = event.entity1.query_components([comp.C_exit])
        self.exit_lst.append(comp_exit.name)

class H_terminate():
    def __init__(self, exit_lst):
        self.exit_lst = exit_lst

    def on_key_event(self, event: core.Key_event):
        if event.key == 27:
            self.exit_lst.append("nagger")

class S_destroy_entity(core.System):
    component_mask = [comp.C_child_of]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler
        self.entites_to_destroy = set()

    def run(self, dt):
        for entity in self.entites_to_destroy:
            entity.destroy_entity()
        self.entites_to_destroy = set()

    def on_destroy_entity_event(self, event: evt.Destroy_entity_event):
        for entity in self.registered_entities:
            [comp_child] = entity.query_components([comp.C_child_of])
            if comp_child.parent.entity_id == event.entity.entity_id:
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))
        self.entites_to_destroy.add(event.entity)

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
            try:
                self.screen.draw_rectangle(comp_trans.x, comp_trans.y, comp_rectangle.width, comp_rectangle.height)
            except:
                pass

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
    def __init__(self, event_handler: core.Event_handler, world):
        self.event_handler = event_handler
        self.world = world
    
    def on_key_event(self, event: core.Key_event):
        if event.key == ord('f'):
            self.event_handler.dispatch_event(evt.Cleanup_event())
        if event.key == ord('g'):
            Object_storage().clone(self.world, "Misc", "Sword", [(0.5, 0.5)])

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
