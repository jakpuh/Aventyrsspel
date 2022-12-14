import sys

sys.path.insert(1, 'core')
import core 
import components as comp
import systems as sys 
import events as evt
from object_storage import Object_storage

class Scene():
    def __init__(self):
        self.world = core.World()
        self.event_handler = core.Event_system()

        collision_system = self.world.add_system(sys.S_collision(self.event_handler))
        tick_system   = self.world.add_system(sys.S_tick(self.event_handler))
        render_system = self.world.add_system(sys.S_render())
        player_system = self.world.add_system(sys.S_player())
        ghost_system = self.world.add_system(sys.S_ghost(self))
        lifetime_system = self.world.add_system(sys.S_lifetime())
        impenetrable_system = self.world.add_system(sys.S_impenetrable())
        # ======== DEBUG =========
        rectangle_system = self.world.add_system(sys.S_debug_render_rectangle())

        player_entity = self.world.create_entity()
        player_entity_components = Object_storage().get("Player", "Default") 
        for component in player_entity_components:
            player_entity.add_component(component)
        [comp_tran] = player_entity.query_components([comp.C_transform])
        comp_tran.x = 0.5
        comp_tran.y = 0.5
        comp_tran.last_y = 0.5
        comp_tran.last_x = 0.5

        ghost_entity = self.world.create_entity()
        ghost_entity_components = Object_storage().get("Monster", "Ghost")
        for component in ghost_entity_components:
            ghost_entity.add_component(component)
        [comp_tran] = ghost_entity.query_components([comp.C_transform])
        comp_tran.x = 0.75
        comp_tran.y = 0.75
        comp_tran.last_x = 0.75
        comp_tran.last_y = 0.75
        # TODO: (maybe) let the user have a range rectangle, instead of every other entity needing to have one (assuming everyone the same range)

        WIDTH = 0.05
        wall_entity = self.clone_entity("Wall", "Default")
        [comp_tran] = wall_entity.query_components([comp.C_transform])
        comp_tran.x = 0.2
        comp_tran.y = 0.2
        comp_tran.last_y = 0.2
        comp_tran.last_x = 0.2

        self.build_border('U', True)
        self.build_border('D', True)
        self.build_border('R', True)
        self.build_border('L', True)

        #self.event_handler.subscribe_event(evt.Tick_event(), render_system.on_tick)
        self.event_handler.subscribe_event(core.Key_event(None), player_system.on_key_event)
        self.event_handler.subscribe_event(evt.Tick_event(), ghost_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Collision_event(None, None), ghost_system.on_collision_event)
        self.event_handler.subscribe_event(evt.Collision_event(None, None), impenetrable_system.on_collision_event)
    
    def clone_entity(self, object_class: str, object_name: str):
        entity = self.world.create_entity()
        entity_components = Object_storage().get(object_class, object_name)
        for component in entity_components:
            entity.add_component(component)
        return entity

    def build_wall_without_door(self, x, y, width, height):
        wall = self.clone_entity("Wall", "Dynamic")
        [comp_tran, comp_box, comp_rect] = wall.query_components([comp.C_transform, comp.C_hitbox, comp.C_rectangle])
        comp_box.h = height
        comp_box.w = width 
        comp_rect.height = height
        comp_rect.width = width
        comp_tran.x = x
        comp_tran.y = y
        comp_tran.last_x = x
        comp_tran.last_y = y
        return wall

    def build_wall_with_door(self, x, y, width, height):
        if width > height:
            self.build_wall_without_door(x, y, width / 2 - 0.025, height)
            self.build_wall_without_door(x + width / 2 + 0.025, y, width / 2 - 0.025, height)
        else:
            self.build_wall_without_door(x, y, width, height / 2 - 0.025)
            self.build_wall_without_door(x, y + height / 2 + 0.025, width, height / 2 - 0.025)

    def build_wall(self, x, y, width, height, has_door):
        if has_door:
            self.build_wall_with_door(x, y, width, height)
            return
        self.build_wall_without_door(x, y, width, height)

    def build_border(self, dir, has_door):
        WIDTH = 0.05
        if dir == 'U':
            self.build_wall(0, 0, 1, WIDTH, has_door)
        elif dir == 'D':
            self.build_wall(0, 1 - WIDTH, 1, WIDTH, has_door)
        elif dir == 'R':
            self.build_wall(1 - WIDTH, WIDTH, WIDTH, 1 - 2 * WIDTH, has_door)
        elif dir == 'L':
            self.build_wall(0, WIDTH, WIDTH, 1 - 2 * WIDTH, has_door)
  
    def run(self, dt):
        core.Screen_wrapper().poll_events(self.event_handler)
        self.world.run(dt)
