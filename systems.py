import core
import components as comp
import curses

class S_render(core.System):
    component_mask = [comp.C_sprite, comp.C_transform]

    def run(self, dt):
        for entity in self.registered_entities:
            pass