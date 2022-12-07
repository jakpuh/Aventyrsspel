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
        # TODO: (maybe) let the user have a range rectangle, instead of every other entity needing to have one (assuming everyone the same range)

        wall_entity = self.world.create_entity()
        wall_entity_components = Object_storage().get("Wall", "Default")
        for component in wall_entity_components:
            wall_entity.add_component(component)
        [comp_tran] = wall_entity.query_components([comp.C_transform])
        comp_tran.x = 0.2
        comp_tran.y = 0.2
        comp_tran.last_y = 0.2
        comp_tran.last_x = 0.2

        north_wall_entity = self.world.create_entity()
        north_wall_entity_components = Object_storage().get("Wall", "Dynamic")
        for component in north_wall_entity_components:
            north_wall_entity.add_component(component)
        [comp_tran] = north_wall_entity.query_components([comp.C_transform])
        comp_tran.x = 0.0
        comp_tran.y = 0.0
        comp_tran.last_y = 0.0
        comp_tran.last_x = 0.0


        #self.event_handler.subscribe_event(evt.Tick_event(), render_system.on_tick)
        self.event_handler.subscribe_event(core.Key_event(None), player_system.on_key_event)
        self.event_handler.subscribe_event(evt.Tick_event(), ghost_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Collision_event(None, None), ghost_system.on_collision_event)
        self.event_handler.subscribe_event(evt.Collision_event(None, None), impenetrable_system.on_collision_event)

    def run(self, dt):
        core.Screen_wrapper().poll_events(self.event_handler)
        self.world.run(dt)
