import core.core as core
import events as evt
import components.components as comp
import math
import random as rand

# Gives xp to the other entity when it kills another entity
class H_xp():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_hit_event(self, event: evt.Hit_event):
        # Assumes the entities have the xp component
        [comp_xp_victim, comp_health] = event.victim_entity.query_components([comp.C_xp, comp.C_health])
        if comp_health.health > 0:
            return
        # Checks if it has parent
        # TODO: don't hardcode in the check for parent
        attacker = event.attacker_entity
        comp_child = attacker.query_components([comp.C_child_of])
        if len(comp_child) == 1:
            attacker = comp_child[0].parent
        [comp_xp_attacker] = attacker.query_components([comp.C_xp])
        comp_xp_attacker.xp += comp_xp_victim.xp

# Sends out tick event every tick
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

# TODO: create system which destroys the entity and use event to call it, instead of directly call destroy_entity. This because we need to also destroy all the children
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

# Checks if entitis collide and sends event
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

# Kills entites when health 0 or below
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

# Delays an action
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

# Switches the rooms
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
            self.exit_lst.append("Terminate")

# Destroyes the entitiy at the end of the frame
class S_destroy_entity(core.System):
    component_mask = [comp.C_child_of]

    def __init__(self, event_handler: core.Event_handler, world):
        super().__init__()
        self.event_handler = event_handler
        self.entites_to_destroy = set()
        self.world = world

    def run(self, dt):
        for entity in self.entites_to_destroy:
            self.world.destroy_entity(entity)
        self.entites_to_destroy = set()

    def on_destroy_entity_event(self, event: evt.Destroy_entity_event):
        for entity in self.registered_entities:
            [comp_child] = entity.query_components([comp.C_child_of])
            if comp_child.parent.entity_id == event.entity.entity_id:
                self.event_handler.dispatch_event(evt.Destroy_entity_event(entity))
        # Save entity_id so the set can remove duplicates
        self.entites_to_destroy.add(event.entity.entity_id)

# =============== DEBUG ===============
class S_debug_player(core.System):
    component_mask = [comp.C_health, comp.C_player]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        for entity in self.registered_entities:
            [comp_health, comp_xp] = entity.query_components([comp.C_health, comp.C_xp])
            self.event_handler.dispatch_event(evt.Log_event("Player_health: ", comp_health.health))
            self.event_handler.dispatch_event(evt.Log_event("Player xp", comp_xp.xp))

class H_debug_keypress():
    def __init__(self, event_handler: core.Event_handler, world):
        self.event_handler = event_handler
        self.world = world
    
    def on_key_event(self, event: core.Key_event):
        if event.key == ord('f'):
            self.event_handler.dispatch_event(evt.Cleanup_event())

class S_disable_children(core.System):
    component_mask = [comp.C_child_of]

    def __init__(self, event_handler: core.Event_handler):
        super().__init__()
        self.event_handler = event_handler

    def run(self, dt):
        pass

    def on_set_children_state_event(self, event: evt.Set_children_state_event):
        for entity in self.registered_entities:
            [comp_child] = entity.query_components([comp.C_child_of])
            if comp_child.parent.entity_id == event.entity.entity_id:
                if event.state == evt.Set_children_state_event.DISABLE:
                    entity.add_component(comp.C_disable())
                    self.event_handler.dispatch_event(evt.Log_event("State", "DISABLED"))
                elif event.state == evt.Set_children_state_event.ENABLE:
                    entity.remove_component(comp.C_disable)
                    self.event_handler.dispatch_event(evt.Log_event("State", "ENABLED"))


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

class H_thorn():
    def __init__(self, event_handler: core.Event_handler):
        self.event_handler = event_handler

    def on_collision_event(self, event: evt.Collision_event):
        # Assumes both entities doesn't have the thorn and health component
        # TODO: call take damage event or something similar and do the checks in the health_system instead
        [comp_thorn] = event.entity1.query_components([comp.C_thorn])
        [comp_health] = event.entity2.query_components([comp.C_health])

        if len(event.entity2.query_components([comp.C_invincible])) == 0:
            comp_health.health -= comp_thorn.damage

            self.event_handler.dispatch_event(evt.Hit_event(event.entity1, event.entity2))
            event.entity2.add_component(comp.C_invincible())
            event.entity2.add_component(comp.C_blink())
            # OBS: INVIC_TIME has to be even, otherwise the player will be invisible when blink components get removed

            remove_actions = [(lambda entity: entity.remove_component(comp.C_invincible), comp_thorn.invinc_ticks),
                              (lambda entity: entity.remove_component(comp.C_blink), comp_thorn.invinc_ticks)]
            self.event_handler.dispatch_event(evt.Log_event("RANDOM", rand.uniform(-1, 1)))
            comp_delay = event.entity2.query_components([comp.C_delay])
            if len(comp_delay) == 0:
                event.entity2.add_component(comp.C_delay(remove_actions))
            else:
                comp_delay[0].actions.extend(remove_actions)
