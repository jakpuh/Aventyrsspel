
import sys

sys.path.insert(1, 'core')
import core
import components as comp
import events as evt

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
            [comp_trans] = entity.query_components([comp.C_transform])
            comp_trans.y += self.KEYMAP[event.key][0] * 0.1
            comp_trans.x += self.KEYMAP[event.key][1] * 0.1

class S_ghost(core.System):
    component_mask = [comp.C_ghost, comp.C_transform]

    def __init__(self):
        super().__init__()
    
    def run(self, dt):
        pass      

    def on_tick_event(event):
        