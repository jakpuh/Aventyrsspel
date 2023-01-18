import core.core as core
import components as comp
import systems as sys 
import events as evt
from object_storage import Object_storage
import math
import utils

class Scene():
    def __init__(self, wall_dirs, screen, left_sidebar, right_sidebar):
        self.world = core.World()
        self.event_handler = core.Event_handler()
        self.exit_lst = []
        self.screen = screen
        self.left_sidebar = left_sidebar
        self.right_sidebar = right_sidebar
        self.walls = {}

        # TODO: use system as a prefix instead of suffix
        animation_system = self.world.add_system(sys.S_animation(self.event_handler))
        follow_system = self.world.add_system(sys.S_follow(self.event_handler, self.screen))
        destroy_entity_system = self.world.add_system(sys.S_destroy_entity(self.event_handler))
        collision_system = self.world.add_system(sys.S_collision(self.event_handler, screen))
        tick_system   = self.world.add_system(sys.S_tick(self.event_handler))
        player_system = self.world.add_system(sys.S_player(self.event_handler, self.world))
        ghost_system = self.world.add_system(sys.S_ghost(self))
        lifetime_system = self.world.add_system(sys.S_lifetime(self.event_handler))
        blink_system = self.world.add_system(sys.S_blink())
        ai_system = self.world.add_system(sys.S_ai(self.event_handler))
        gangster_system = self.world.add_system(sys.S_gangster(self.event_handler, self))
        monkey_system = self.world.add_system(sys.S_monkey(self.event_handler, self.world))
        bullet_system = self.world.add_system(sys.S_bullet(self.event_handler))
        void_system = self.world.add_system(sys.S_void(self.event_handler, screen))
        bomb_system = self.world.add_system(sys.S_bomb(self.event_handler, self.world))
        boomer_system = self.world.add_system(sys.S_boomer(self.event_handler, self.world))
        fox_system = self.world.add_system(sys.S_fox(self.event_handler))
        death_system = self.world.add_system(sys.S_death(self.event_handler))
        delay_system = self.world.add_system(sys.S_delay(self.event_handler))
        impenetrable_system = self.world.add_system(sys.S_impenetrable(self.event_handler))
        shoot_system = self.world.add_system(sys.S_shoot(self.event_handler, self.world))
        throw_bombs_system = self.world.add_system(sys.S_throw_bombs(self.event_handler, self.world))
        chest_system = self.world.add_system(sys.S_chest(self.event_handler, self.world))

        # ======== DEBUG =========
        rectangle_system = self.world.add_system(sys.S_debug_render_rectangle(screen))
        player_debug_system = self.world.add_system(sys.S_debug_player(self.event_handler))
        keypress_debug_handler = sys.H_debug_keypress(self.event_handler, self.world)
        # text_system = self.world.add_system(sys.S_debug_render_text(right_sidebar))
        log_system = self.world.add_system(sys.S_logging(right_sidebar))

        terminate_handler = sys.H_terminate(self.exit_lst)
        exit_handler = sys.H_exit(self.exit_lst)
        thorn_handler = sys.H_thorn(self.event_handler)
        enemythorn_handler = sys.H_enemythorn(self.event_handler)
        scout_handler = sys.H_scout(self.event_handler)

        render_system = self.world.add_system(sys.S_render(screen))

        self.event_handler.subscribe_event(core.Key_event, player_system.on_key_event)
        self.event_handler.subscribe_event(core.Key_event, terminate_handler.on_key_event)
        self.event_handler.subscribe_event(core.Key_event, keypress_debug_handler.on_key_event)
        self.event_handler.subscribe_event(evt.Tick_event, blink_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, shoot_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, ai_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, monkey_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, bomb_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, throw_bombs_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, fox_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, animation_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, lifetime_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, delay_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Tick_event, player_system.on_tick_event)
        self.event_handler.subscribe_event(evt.Log_event, log_system.on_log_event)
        # self.event_handler.subscribe_event(evt.Collision_event, ghost_system.on_collision_event, utils.collision_event_pred_generator([comp.C_player, comp.C_transform], [comp.C_scout, comp.C_child_of]))
        self.event_handler.subscribe_event(evt.Collision_event, monkey_system.on_collision_event, utils.collision_event_pred_generator([comp.C_player, comp.C_transform], [comp.C_scout, comp.C_child_of]))
        self.event_handler.subscribe_event(evt.Collision_event, impenetrable_system.on_collision_event, utils.collision_event_pred_generator([comp.C_impenetrable], [comp.C_transform]))
        self.event_handler.subscribe_event(evt.Collision_event, exit_handler.on_collision_event, utils.collision_event_pred_generator([comp.C_exit], [comp.C_player]))
        self.event_handler.subscribe_event(evt.Collision_event, thorn_handler.on_collision_event, utils.collision_event_pred_generator([comp.C_thorn], [comp.C_health]))
        self.event_handler.subscribe_event(evt.Collision_event, fox_system.on_collision_event, utils.collision_event_pred_generator([comp.C_player, comp.C_transform], [comp.C_scout, comp.C_child_of]))
        self.event_handler.subscribe_event(evt.Collision_event, bullet_system.on_collision_event, utils.collision_event_pred_generator([comp.C_bullet], [comp.C_impenetrable]))
        self.event_handler.subscribe_event(evt.Collision_event, enemythorn_handler.on_collision_event, utils.collision_event_pred_generator([comp.C_enemythorn], [comp.C_health]))
        pred = lambda event: (utils.collision_event_pred_generator([comp.C_child_of, comp.C_scout], [comp.C_enemy])(event) and utils.collision_event_pred_generator_parent([comp.C_friend], None)(event)) or\
                             (utils.collision_event_pred_generator([comp.C_child_of, comp.C_scout], [comp.C_friend])(event) and utils.collision_event_pred_generator_parent([comp.C_enemy], None)(event))
        self.event_handler.subscribe_event(evt.Collision_event, scout_handler.on_collision_event, pred)
        self.event_handler.subscribe_event(evt.Collision_event, chest_system.on_collision_event, utils.collision_event_pred_generator([comp.C_chest], [comp.C_health]))
        self.event_handler.subscribe_event(evt.Cleanup_event, blink_system.on_cleanup_event)
        self.event_handler.subscribe_event(evt.Cleanup_event, bullet_system.on_cleanup_event)
        self.event_handler.subscribe_event(evt.Cleanup_event, delay_system.on_cleanup_event)
        self.event_handler.subscribe_event(evt.Destroy_entity_event, destroy_entity_system.on_destroy_entity_event)
        self.event_handler.subscribe_event(evt.Target_event, ghost_system.on_target_event)
        self.event_handler.subscribe_event(evt.Target_event, shoot_system.on_target_event)
        self.event_handler.subscribe_event(evt.Add_component, shoot_system.on_add_component_event)

        all_dirs = ['U', 'D', 'L', 'R']
        no_wall_dirs = list(set(wall_dirs)^set(all_dirs))

        for dir in wall_dirs:
            self.build_border(dir, True)
        for dir in no_wall_dirs:
            self.build_border(dir, False)

    def build_wall_with_door(self, x, y, width, height, name_of_exit, door_width = 0.05):
        if width > height:
            Object_storage().clone(self.world, "Wall", "Dynamic", [(x, y), (width / 2 - door_width, height)])
            Object_storage().clone(self.world, "Misc", "Exit", [name_of_exit, (x + width / 2 - door_width, y), (door_width * 2, height)])
            Object_storage().clone(self.world, "Wall", "Dynamic", [(x + width / 2 + door_width, y), (width / 2 - door_width, height)])
        else:
            Object_storage().clone(self.world, "Wall", "Dynamic", [(x, y), (width, height / 2 - door_width)])
            Object_storage().clone(self.world, "Misc", "Exit", [name_of_exit, (x, y + height / 2 - door_width), (width, door_width * 2)])
            Object_storage().clone(self.world, "Wall", "Dynamic", [(x, y + height / 2 + door_width), (width, height / 2 - door_width)])

    def build_wall(self, x, y, width, height, has_door, name_of_exit):
        if has_door:
            return self.build_wall_with_door(x, y, width, height, name_of_exit)
        return Object_storage().clone(self.world, "Wall", "Dynamic", [(x, y), (width, height)])

    def build_border(self, dir, has_door):
        WIDTH = 0.05
        if dir == 'U':
            self.walls[dir] = self.build_wall(0, 0, 1, WIDTH, has_door, 'U')
        elif dir == 'D':
            self.walls[dir] = self.build_wall(0, 1 - WIDTH, 1, WIDTH, has_door, 'D')
        elif dir == 'R':
            self.walls[dir] = self.build_wall(1 - WIDTH, WIDTH, WIDTH, 1 - 2 * WIDTH, has_door, 'R')
        elif dir == 'L':
            self.walls[dir] = self.build_wall(0, WIDTH, WIDTH, 1 - 2 * WIDTH, has_door, 'L')
  
    def run(self, dt) -> list[str]:
        del self.exit_lst[:]
        core.screen.poll_events(self.event_handler)
        self.world.run(dt)
        return self.exit_lst

    # cleans the rooms before a switch
    def cleanup(self):
        self.event_handler.dispatch_event(evt.Cleanup_event())

class Challenge_scene(Scene):
    def __init__(self, wall_dirs, screen, left_sidebar, right_sidebar, difficulty = 0):
        super().__init__(wall_dirs, screen, left_sidebar, right_sidebar)

        Object_storage().clone(self.world, "Monster", "Ghost", [(0.75, 0.75)])
        Object_storage().clone(self.world, "Monster", "Gangster", [(0.25, 0.75)])
        Object_storage().clone(self.world, "Monster", "Boomer", [(0.5, 0.2)])
        Object_storage().clone(self.world, "Monster", "Monkey", [(0.2, 0.2)])
        Object_storage().clone(self.world, "Monster", "Fox", [(0.75, 0.2)])

        Object_storage().clone(self.world, "Projectile", "Bullet", [0.1, (0.75, 0.25)])
        Object_storage().clone(self.world, "Projectile", "Bomb", [(0.5, 0.5), 0.1, 20])
        Object_storage().clone(self.world, "Misc", "Sword", [(0.5, 0.7)])
        Object_storage().clone(self.world, "Misc", "Chest", [(0.5, 0.8)])

                
class Puzzle_scene(Scene):
    def __init__(self, wall_dirs, screen, left_sidebar, right_sidebar, difficulty = 0):
        super().__init__(wall_dirs, screen, left_sidebar, right_sidebar)

class Boss_scene(Scene):
    def __init__(self, wall_dirs, exit_side, screen, left_sidebar, right_sidebar, difficulty = 0):
        super().__init__(wall_dirs, screen, left_sidebar, right_sidebar)
        self.exit_side = exit_side

        gm_boss_system = self.world.add_system(sys.S_gm_boss(self.event_handler))
        self.event_handler.subscribe_event(evt.Destroy_entity_event, gm_boss_system.on_destroy_entity_event)

        Object_storage().clone(self.world, "GameManager", "Boss", [lambda: (self.walls[exit_side].destroy_entity(),
                                                                            self.build_exit_border(exit_side))])
        Object_storage().clone(self.world, "Monster", "Monkey", [(0.5, 0.5)])

    def build_exit_border(self, dir):
        WIDTH = 0.05
        DOOR_WIDTH = 0.1
        match dir:
            case 'U':
                self.walls[dir] = self.build_wall_with_door(0, 0, 1, WIDTH, 'exit', DOOR_WIDTH)
            case 'D':
                self.walls[dir] = self.build_wall_with_door(0, 1 - WIDTH, 1, WIDTH, 'exit', DOOR_WIDTH)
            case 'R':
                self.walls[dir] = self.build_wall_with_door(1 - WIDTH, WIDTH, WIDTH, 1 - 2 * WIDTH, 'exit', DOOR_WIDTH)
            case 'L':
                self.walls[dir] = self.build_wall_with_door(0, WIDTH, WIDTH, 1 - 2 * WIDTH, 'exit', DOOR_WIDTH)
            
class Empty_scene(Scene):
    def __init__(self, wall_dirs, screen, left_sidebar, right_sidebar, difficulty = 0):
        super().__init__(wall_dirs, screen, left_sidebar, right_sidebar)