import core.core as core
import components.components as comp
import events as evt

# Renders the sprites
class S_render(core.System):
    component_mask = [comp.C_sprite, comp.C_transform]

    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def run(self, dt):
        self.screen.refresh()
        for entity in self.registered_entities:
            [comp_sprite, comp_trans] = entity.query_components([comp.C_sprite, comp.C_transform])
            if comp_sprite.texture == None:
                continue
            try:
                self.screen.draw_texture(comp_sprite.texture, comp_trans.x, comp_trans.y)
            except:
                pass

# Makes the sprite blink
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

# Switchs between sprites 
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

class S_print_text(core.System):
    component_mask = [comp.C_none]

    def __init__(self, left_panel: core.Window, right_panel: core.Window):
        super().__init__()
        self.left_panel = left_panel
        self.right_panel = right_panel
        self.d = {}

    def on_print_event(self, event: evt.Log_event):
        self.d[event.key] = (event.value, event.right_sidebar)

    def run(self, dt):
        i = 0.02
        for key, (value, is_right) in self.d.items():
            if is_right:
                self.right_panel.draw_text(0, i, "  " + str(key) + ": " + str(value))
            else:
                self.left_panel.draw_text(0, i, "  " + str(key) + ": " + str(value))
            i += 0.05
        self.left_panel.refresh()
        self.right_panel.refresh()

# =========== DEBUG =============
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