# TODO: use a registered function when component_mask gets updated
import sys

sys.path.insert(1, 'core')
import core
import components as comp
import events as evt
from object_storage import Object_storage

class S_tick(core.System):
    component_mask = [None]
    def __init__(self, event_handler):
        super().__init__() 
        self.event_handler = event_handler 
        self.tot_dt = 0

    def run(self, dt):
        if (self.tot_dt >= 0.05):
            self.event_handler.dispatch_event(evt.Tick_event())
            self.tot_dt = 0
        else:
            self.tot_dt += dt

class S_render(core.System):
    component_mask = [comp.C_sprite, comp.C_transform]

    def __init__(self):
        super().__init__()

    def run(self, dt):
        core.Screen_wrapper().refresh()
        print(dt)
        for entity in self.registered_entities:
            [comp_sprite, comp_trans] = entity.query_components([comp.C_sprite, comp.C_transform])
            core.Screen_wrapper().draw_texture(comp_sprite.texture, comp_trans.x, comp_trans.y)

class S_player(core.System):
    component_mask = [comp.C_player, comp.C_transform]
    KEYMAP = {
        ord('w'): [-1, 0],
        ord('d'): [0, 1],
        ord('s'): [1, 0],
        ord('a'): [0, -1]
    }

    def __init__(self):
        super().__init__()

    def run(self, dt):
        pass

    # refactor screen_wrapper; don't use event handler
    # move this to the run function
    def on_key_event(self, event: core.Key_event):
        if not event.key in self.KEYMAP:
            return
        for entity in self.registered_entities:
            print(len(self.registered_entities))
            [comp_trans] = entity.query_components([comp.C_transform])
            comp_trans.y += self.KEYMAP[event.key][0] * 0.1
            comp_trans.x += self.KEYMAP[event.key][1] * 0.1

class S_ghost(core.System):
    component_mask = [comp.C_ghost, comp.C_transform]
    def __init__(self, world):
        super().__init__()
        self.world = world
    
    def run(self, dt):
        for entity in self.registered_entities:
            [comp_ghost, comp_tran] = entity.query_components([comp.C_ghost, comp.C_transform])
            if comp_ghost.target == None:
                continue
            comp_tran.x += comp_ghost.target[0] * comp_ghost.speed * dt
            comp_tran.y += comp_ghost.target[1] * comp_ghost.speed * dt

    def on_tick_event(self, event):
        # TODO: Maybe create a box with a hitbox
        #       when player in box -> event will get called
        for entity in self.registered_entities:
            [tran_comp] = entity.query_components([comp.C_transform])

            range_entity = self.world.create_entity()
            range_entity.add_component(comp.C_child_of(entity)) 
            range_entity.add_component(comp.C_lifetime(2)) 
            range_entity.add_component(comp.C_hitbox(40, 40)) 
            range_entity.add_component(comp.C_transform(tran_comp.x, tran_comp.y)) 
            range_entity.add_component(comp.C_range())

    def on_collision_event(self, event):
        entity1_range = event.entity1.query_components([comp.C_range, comp.C_child_of]) 
        entity2_range = event.entity2.query_components([comp.C_range, comp.C_child_of])
        entity1_player = event.entity1.query_components([comp.C_player, comp.C_transform])
        entity2_player = event.entity2.query_components([comp.C_player, comp.C_transform])
        if len(entity1_range) == 2 and len(entity2_player) == 2:
            comp_ghost = self.world.query_components(entity1_range[1].parent, [comp.C_ghost])
            if len(comp_ghost) == 0:
                return
            comp_ghost[0].target = [entity2_player[1].x, entity2_player[1].y]
        elif len(entity1_player) == 2 and len(entity2_range) == 2:
            comp_ghost = self.world.query_components(entity2_range[1].parent, [comp.C_ghost])
            if len(comp_ghost) == 0:
                return
            comp_ghost[0].target = [entity1_player[1].x, entity1_player[1].y]

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
    def __init__(self, event_handler):
        super().__init__()
        self.event_handler = event_handler

    # TODO: don't send out event twice
    def run(self, dt):
        for entity1 in self.registered_entities:
            for entity2 in self.registered_entities:
                [hit_comp1, tran_comp1] = entity1.query_components([comp.C_hitbox, comp.C_transform])
                [hit_comp2, tran_comp2] = entity2.query_components([comp.C_hitbox, comp.C_transform])
                if tran_comp1.x < hit_comp2.w + tran_comp2.x and \
                    tran_comp1.x + hit_comp1.w > tran_comp2.x and \
                    tran_comp1.y > hit_comp2.h + tran_comp2.y and \
                    tran_comp1.y + hit_comp1.h < tran_comp2.y: \
                    self.event_handler.dispatch_event(entity1, entity2)

