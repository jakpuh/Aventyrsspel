import sys

sys.path.insert(1, 'core')
import core 
import components as comp
import systems as sys 
import events as evt

class Scene():
    def __init__(self):
        self.world = core.World()
        self.event_handler = core.Event_system()

        tick_system   = self.world.add_system(sys.S_tick(self.event_handler))
        render_system = self.world.add_system(sys.S_render())
        player_system = self.world.add_system(sys.S_player())

        entity = self.world.create_entity()
        entity.add_component(comp.C_player())
        entity.add_component(comp.C_transform(0.5, 0.5))
        entity.add_component(comp.C_hitbox(1, 1))
        entity.add_component(comp.C_health(10))
        entity.add_component(comp.C_sprite("#"))

        #self.event_handler.subscribe_event(evt.Tick_event(), render_system.on_tick)
        self.event_handler.subscribe_event(core.Key_event(None), player_system.on_key_event)

    def run(self, dt):
        core.Screen_wrapper().poll_events(self.event_handler)
        self.world.run(dt)
