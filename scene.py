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

        tick_system   = self.world.add_system(sys.S_tick(self.event_handler))
        render_system = self.world.add_system(sys.S_render())
        player_system = self.world.add_system(sys.S_player())

        player_entity = self.world.create_entity()
        player_entity_components = Object_storage().get("Player", "Default") 
        for component in player_entity_components:
            player_entity.add_component(component)
        [comp_tran] = player_entity.query_components([comp.C_transform])
        comp_tran.x = 0.5
        comp_tran.y = 0.5

        #self.event_handler.subscribe_event(evt.Tick_event(), render_system.on_tick)
        self.event_handler.subscribe_event(core.Key_event(None), player_system.on_key_event)

    def run(self, dt):
        core.Screen_wrapper().poll_events(self.event_handler)
        self.world.run(dt)
