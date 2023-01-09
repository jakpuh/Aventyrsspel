import sys

sys.path.insert(1, 'core')
import core 
import components as comp
import systems as sys 
import events as evt
from object_storage import Object_storage
import math
import utils

class Scene():
    def build_wall_with_door(self, x, y, width, height, name_of_exit):
        DOOR_WIDTH = 0.05   # Is actually half the width of the door because it reduces the complexity of the following expressions
        if width > height:
            Object_storage().clone(self.world, "Wall", "Dynamic", [(x, y), (width / 2 - DOOR_WIDTH, height)])
            Object_storage().clone(self.world, "Misc", "Exit", [name_of_exit, (x + width / 2 - DOOR_WIDTH, y), (DOOR_WIDTH * 2, height)])
            Object_storage().clone(self.world, "Wall", "Dynamic", [(x + width / 2 + DOOR_WIDTH, y), (width / 2 - DOOR_WIDTH, height)])
        else:
            Object_storage().clone(self.world, "Wall", "Dynamic", [(x, y), (width, height / 2 - DOOR_WIDTH)])
            Object_storage().clone(self.world, "Misc", "Exit", [name_of_exit, (x, y + height / 2 - DOOR_WIDTH), (width, DOOR_WIDTH * 2)])
            Object_storage().clone(self.world, "Wall", "Dynamic", [(x, y + height / 2 + DOOR_WIDTH), (width, height / 2 - DOOR_WIDTH)])

    def build_wall(self, x, y, width, height, has_door, name_of_exit):
        if has_door:
            self.build_wall_with_door(x, y, width, height, name_of_exit)
            return
        Object_storage().clone(self.world, "Wall", "Dynamic", [(x, y), (width, height)])

    def build_border(self, dir, has_door):
        WIDTH = 0.05
        if dir == 'U':
            self.build_wall(0, 0, 1, WIDTH, has_door, 'U')
        elif dir == 'D':
            self.build_wall(0, 1 - WIDTH, 1, WIDTH, has_door, 'D')
        elif dir == 'R':
            self.build_wall(1 - WIDTH, WIDTH, WIDTH, 1 - 2 * WIDTH, has_door, 'R')
        elif dir == 'L':
            self.build_wall(0, WIDTH, WIDTH, 1 - 2 * WIDTH, has_door, 'L')
  
    def run(self, dt) -> list[str]:
        del self.exit_lst[:]
        # core.Screen_wrapper().poll_events(self.event_handler)
        core.screen.poll_events(self.event_handler)
        self.world.run(dt)
        return self.exit_lst

    # cleans the rooms before a switch
    def cleanup(self):
        self.event_handler.dispatch_event(evt.Cleanup_event())

class Challenge_scene(Scene):
    def __init__(self, wall_dirs, screen, left_sidebar, right_sidebar):
        self.world = core.World()
        self.event_handler = core.Event_handler()
        self.exit_lst = []
        self.screen = screen
        self.left_sidebar = left_sidebar
        self.right_sidebar = right_sidebar

        # TODO: use system as a prefix instead of suffix
        collision_system = self.world.add_system(sys.S_collision(self.event_handler, screen))
        tick_system   = self.world.add_system(sys.S_tick(self.event_handler))
        render_system = self.world.add_system(sys.S_render(screen))
        player_system = self.world.add_system(sys.S_player(self.event_handler))
        ghost_system = self.world.add_system(sys.S_ghost(self))
        lifetime_system = self.world.add_system(sys.S_lifetime())
        impenetrable_system = self.world.add_system(sys.S_impenetrable())
        blink_system = self.world.add_system(sys.S_blink())
        ai_system = self.world.add_system(sys.S_ai(self.event_handler))
        gangster_system = self.world.add_system(sys.S_gangster(self.event_handler, self))
        bullet_system = self.world.add_system(sys.S_bullet(self.event_handler))
        range_system = self.world.add_system(sys.S_range(self.event_handler))
        # ======== DEBUG =========
        rectangle_system = self.world.add_system(sys.S_debug_render_rectangle(screen))
        player_debug_system = self.world.add_system(sys.S_debug_player(self.event_handler))
        keypress_debug_handler = sys.H_debug_keypress(self.event_handler)
        # text_system = self.world.add_system(sys.S_debug_render_text(right_sidebar))
        log_system = self.world.add_system(sys.S_logging(right_sidebar))

        exit_handler = sys.H_exit(self.exit_lst)
        thorn_handler = sys.H_thorn(self.event_handler)
        delay_handler = sys.H_delay()

        Object_storage().clone(self.world, "Monster", "Ghost", [(0.75, 0.75)])
        Object_storage().clone(self.world, "Monster", "Gangster", [(0.25, 0.75)])
        Object_storage().clone(self.world, "Monster", "Monkey", [(0.2, 0.2)])

        Object_storage().clone(self.world, "Projectile", "Bullet", [0.1, (0.75, 0.25)])

        all_dirs = ['U', 'D', 'L', 'R']
        no_wall_dirs = list(set(wall_dirs)^set(all_dirs))

        for dir in wall_dirs:
            self.build_border(dir, True)
        for dir in no_wall_dirs:
            self.build_border(dir, False)

        self.event_handler.subscribe_event(core.Key_event, player_system.on_key_event)
        self.event_handler.subscribe_event(core.Key_event, keypress_debug_handler.on_key_event)
        self.event_handler.subscribe_event(evt.Tick_event, delay_handler.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, blink_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, gangster_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, ai_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Log_event, log_system.on_log_event)
        self.event_handler.subscribe_event(evt.Collision_event, ghost_system.on_collision_event, utils.collision_event_pred_generator([comp.C_player, comp.C_transform], [comp.C_range, comp.C_child_of]))
        self.event_handler.subscribe_event(evt.Collision_event, gangster_system.on_collision_event, utils.collision_event_pred_generator([comp.C_player, comp.C_transform], [comp.C_range, comp.C_child_of]))
        self.event_handler.subscribe_event(evt.Collision_event, impenetrable_system.on_collision_event, utils.collision_event_pred_generator([comp.C_impenetrable], [comp.C_transform]))
        self.event_handler.subscribe_event(evt.Collision_event, exit_handler.on_collision_event, utils.collision_event_pred_generator([comp.C_exit], [comp.C_player]))
        self.event_handler.subscribe_event(evt.Collision_event, thorn_handler.on_collision_event, utils.collision_event_pred_generator([comp.C_thorn], [comp.C_health]))
        self.event_handler.subscribe_event(evt.Collision_event, bullet_system.on_collision_event, utils.collision_event_pred_generator([comp.C_bullet], [comp.C_impenetrable]))
        self.event_handler.subscribe_event(evt.Delay_event, delay_handler.on_delay_event)
        self.event_handler.subscribe_event(evt.Cleanup_event, blink_system.on_cleanup_event)
        self.event_handler.subscribe_event(evt.Cleanup_event, delay_handler.on_cleanup_event)
        self.event_handler.subscribe_event(evt.Cleanup_event, bullet_system.on_cleanup_event)

class Puzzle_scene(Scene):
    pass