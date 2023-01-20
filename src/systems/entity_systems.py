import core.core as core
import events as evt
import components.components as comp
import math
import random as rand
from object_storage import Object_storage

# Takes care of the player movement and attack
class S_player(core.System):
    component_mask = [comp.C_player, comp.C_transform, comp.C_health, comp.C_xp]

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
            [comp_health, comp_xp, comp_player] = entity.query_components([comp.C_health, comp.C_xp, comp.C_player])

            self.event_handler.dispatch_event(evt.Print_event("Health", comp_health.health, True))
            self.event_handler.dispatch_event(evt.Print_event("Damage", math.ceil(comp_player.damage), True))
            self.event_handler.dispatch_event(evt.Print_event("Score", comp_xp.xp, True))

    def on_tick_event(self, event):
        for entity in self.registered_entities:
            [comp_player]  = entity.query_components([comp.C_player])
            comp_player.attack_cooldown = max(comp_player.attack_cooldown - 1, 0)

    def _attack(self):
        for entity in self.registered_entities:
            [comp_player] = entity.query_components([comp.C_player])
            if comp_player.attack_cooldown > 0:
                continue
            Object_storage().clone(self.world, "Misc", "Spinning-swords", [entity, comp_player.damage])
            comp_player.attack_cooldown = comp.C_player.ATTACK_COOLDOWN

    # refactor screen_wrapper; don't use event handler
    # move this to the run function
    def on_key_event(self, event: core.Key_event):
        if event.key == ord(' '):
            self._attack()
        if not event.key in self.KEYMAP:
            return
        for entity in self.registered_entities:
            [comp_trans, comp_player] = entity.query_components([comp.C_transform, comp.C_player])
            # TODO: define speed in Player component
            comp_trans.last_x = comp_trans.x
            comp_trans.last_y = comp_trans.y
            comp_trans.y += self.KEYMAP[event.key][0] * comp_player.speed
            comp_trans.x += self.KEYMAP[event.key][1] * comp_player.speed

# Gives the entity increased strength, speed and health when touching a chest
class H_chest():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_collision_event(self, event: evt.Collision_event):
        [comp_chest] = event.entity1.query_components([comp.C_chest])
        [comp_health, comp_player] = event.entity2.query_components([comp.C_health, comp.C_player])

        comp_health.health += comp_chest.health
        comp_player.damage += comp_chest.damage
        comp_player.speed = min(comp_player.speed + comp_chest.speed, 0.03)
        self.event_handler.dispatch_event(evt.Destroy_entity_event(event.entity1))

# Checks if a entity is inside the scouting area
class H_scout():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_collision_event(self, event: evt.Collision_event):
        # TODO: "ignore" entities with disable component in ecs instead of doing this
        if len(event.entity1.query_components([comp.C_disable])) == 1:
            return

        self.event_handler.dispatch_event(evt.Log_event("scout", rand.uniform(-1, 1)))
        [comp_child] = event.entity1.query_components([comp.C_child_of])
        [comp_tran] = event.entity2.query_components([comp.C_transform])
        comp_child.parent.add_component(comp.C_target((comp_tran.x, comp_tran.y)))
        if (len(comp_child.parent.query_components([comp.C_target])) == 0):
            self.event_handler.dispatch_event(evt.Add_component_event(comp.C_target, comp_child.parent))
        self.event_handler.dispatch_event(evt.Target_event(comp_child.parent))

# Moves the ghost after the player
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

# Shoots against target
class S_shoot(core.System):
    component_mask = [comp.C_shoot, comp.C_transform, comp.C_target]

    def __init__(self, event_handler: core.Event_handler, world: core.World, difficulty):
        super().__init__()
        self.event_handler = event_handler
        self.world = world
        self.difficulty = difficulty

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
            Object_storage().clone(self.world, "Projectile", "Bullet", [dir, (comp_tran.x, comp_tran.y), self.difficulty])

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

        event.entity.remove_component(comp.C_ai) 

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

        self._delay_next_shoot(event.entity, comp_shoot[0].fire_rate)

# Places random bombs in the room
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

    def on_reset_event(self, event: evt.Reset_event):
        if event.component != comp.C_throw_bombs:
            return
        
        [comp_delay] = event.entity.query_components([comp.C_delay])
        actions = {
            "Add-throw_bombs": (lambda _: None, 0)
        }
        comp_delay.named_actions.update(actions)
        event.entity.remove_component(comp.C_throw_bombs)

# Handles the switching between dashing and ai
class H_dasher():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_trigger_event(self, event: evt.Trigger_event):
        comps = event.entity.query_components([comp.C_dasher, comp.C_target])
        if len(comps) != 2:
            return

        # TODO: remove components from the disable components list in the ecs
        # TODO: fix this
        event.entity.enable_components([comp.C_dash])
        [comp_delay, comp_dash] = event.entity.query_components([comp.C_delay, comp.C_dash])
        event.entity.disable_components([comp.C_dash])

        actions = {
            "Dash": (lambda entity: (entity.enable_components([comp.C_dash]),
                                     self.event_handler.dispatch_event(evt.Set_children_state_event(entity, evt.Set_children_state_event.DISABLE))), 
                                     comp_dash.recovery_time)
        }
        comp_delay.named_actions.update(actions)

        event.entity.disable_group([comp.C_ai], "AI")
        event.entity.disable_group([event.trigger_type], "Trigger")
    
    def on_finished_event(self, event: evt.Finished_event):
        comps = event.entity.query_components([comp.C_dasher])
        if len(comps) == 0 or event.component != comp.C_dash:
            return
        
        [comp_delay, comp_dash] = event.entity.query_components([comp.C_delay, comp.C_dash])
        self.event_handler.dispatch_event(evt.Set_children_state_event(event.entity, evt.Set_children_state_event.ENABLE))
        actions = {
            "Trigger": (lambda entity: (entity.enable_group("AI"), entity.enable_group("Trigger")), comp_dash.recovery_time)
        }
        comp_delay.named_actions.update(actions)

        event.entity.remove_component(comp.C_target)
        event.entity.disable_components([comp.C_dash])

    def on_reset_event(self, event: evt.Reset_event):
        if event.component != comp.C_dasher:
            return

        [comp_delay] = event.entity.query_components([comp.C_delay])
        actions = {
            "Dash": (lambda _: None, 0),
            "Trigger": (lambda _: None, 0)
        }
        comp_delay.named_actions.update(actions)

        self.event_handler.dispatch_event(evt.Set_children_state_event(event.entity, evt.Set_children_state_event.ENABLE))
        event.entity.enable_group("AI")
        event.entity.remove_component(comp.C_target)
        event.entity.remove_component(comp.C_dash)
        event.entity.remove_component(comp.C_dasher)

# Dashes towards the player
class S_dash(core.System):
    component_mask = [comp.C_dash, comp.C_transform, comp.C_target]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_dash, comp_tran, comp_target] = entity.query_components([comp.C_dash, comp.C_transform, comp.C_target])
            if abs(comp_tran.x - comp_target.target[0]) < comp_dash.speed * dt and abs(comp_tran.y - comp_target.target[1]) < comp_dash.speed * dt or\
                    (comp_tran.last_x == comp_tran.x and comp_tran.last_y == comp_tran.y):
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

    def on_collision_event(self, event: evt.Collision_event):
        self.event_handler.dispatch_event(evt.Finished_event(event.entity1, comp.C_dash))

# Boss fight 
class S_monkey(core.System):
    component_mask = [comp.C_monkey, comp.C_transform, comp.C_health]

    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.world = world

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        # TODO: make handler which creates the entity for you
        for entity in self.registered_entities:
            [comp_health, comp_monkey] = entity.query_components([comp.C_health, comp.C_monkey])

            # TODO: add delay between boss phases
            if comp_health.health > 12: 
                if comp_monkey.phase_state == None:
                    entity.add_component(comp.C_dasher())
                    comp_monkey.phase_state = comp.C_monkey.PHASE_1
            elif comp_health.health > 6:
                if comp_monkey.phase_state == comp.C_monkey.PHASE_1:
                    self.event_handler.dispatch_event(evt.Reset_event(entity, comp.C_dasher))
                    comp_monkey.phase_state = comp.C_monkey.PHASE_2
                    entity.enable_components([comp.C_throw_bombs])
            elif comp_health.health > 0:
                if comp_monkey.phase_state == comp.C_monkey.PHASE_2:
                    self.event_handler.dispatch_event(evt.Reset_event(entity, comp.C_throw_bombs))
                    comp_monkey.phase_state = comp.C_monkey.PHASE_3
                    entity.enable_components([comp.C_shoot])

# Handles a bomb before explosion
class S_bomb(core.System):
    component_mask = [comp.C_bomb, comp.C_transform]
    
    def __init__(self, event_handler: core.Event_handler, world, difficulty):
        super().__init__()
        self.event_handler = event_handler
        self.world = world
        self.difficulty = difficulty

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [comp_tran, comp_bomb] = entity.query_components([comp.C_transform, comp.C_bomb])
            if comp_bomb.det_time <= 0:
                Object_storage().clone(self.world, "Misc", "Explosion", [(comp_tran.x - comp_bomb.radius, comp_tran.y - comp_bomb.radius), comp_bomb.radius, self.difficulty])
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))
                continue
            comp_bomb.det_time -= 1

# Follows the parent around
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

# Goes towards dir
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

# Goes to random places
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

# Kills entity after x ticks
class S_lifetime(core.System):
    component_mask = [comp.C_lifetime]
    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        pass

    def on_tick_event(self, event: evt.Tick_event):
        for entity in self.registered_entities:
            [life_comp] = entity.query_components([comp.C_lifetime])
            if life_comp.lifetime == 0:
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))
            life_comp.lifetime -= 1

class C_transform(core.Component):
    def __init__(self, x, y):
        # used to revert position when colliding with a wall
        self.last_x = x 
        self.last_y = y
        self.x = x
        self.y = y