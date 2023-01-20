from dungeon_generator import *
from dungeon_generator_algorithm import *
import time
import components.components as comp
import events as evt
from object_storage_builder import Object_storage
import object_storage_builder as storage_builder
import core.core as core

class Game_manager(metaclass=core.Singleton):
    '''
    Game_manager is a global singleton class which has the responsibility to control the high level aspects of the games loop.
    '''
    POS = {
        'U': (0.8, None),
        'D': (0.2, None),
        'R': (None, 0.2),
        'L': (None, 0.8)
    }
    FPS = 30

    def __init__(self):
        '''
        Init inits stuff which only should be initialized once per the lifetime of the application
        '''
        storage_builder.fill_object_storage()
    
    def _clone_players(self, room, next_room):
        player_entities = room.scene.world.get_entities([comp.C_player])
        for player in player_entities:
            player_components = player.query_components_all()
            new_player = next_room.scene.world.create_entity()
            for player_component in player_components:
                new_player.add_component(player_component)
            [tran_comp] = new_player.query_components([comp.C_transform])
            tran_comp.y = 0.5
            tran_comp.x = 0.5
            tran_comp.last_y = 0.5
            tran_comp.last_x = 0.5
            room.scene.event_handler.dispatch_event(evt.Destroy_entity_event(player))

    def _move_players(self, rooms, current_room, dir):
        # Move the players into the next room
        next_room = rooms[current_room].neighbours[dir]
        player_entities = rooms[current_room].scene.world.get_entities([comp.C_player])
        for player in player_entities:
            player_components = player.query_components_all()
            new_player = rooms[next_room].scene.world.create_entity()
            for player_component in player_components:
                new_player.add_component(player_component)
            [tran_comp] = new_player.query_components([comp.C_transform])
            tran_comp.y = self.POS[dir][0] if self.POS[dir][0] != None else tran_comp.y
            tran_comp.x = self.POS[dir][1] if self.POS[dir][1] != None else tran_comp.x
            tran_comp.last_y = self.POS[dir][0] if self.POS[dir][0] != None else tran_comp.y
            tran_comp.last_x = self.POS[dir][1] if self.POS[dir][1] != None else tran_comp.x
            rooms[current_room].scene.event_handler.dispatch_event(evt.Destroy_entity_event(player))
        return next_room
    
    def _run(self, layout_generator = Layout_generator_spanning):
        main_window = core.screen.create_window(0.15, 0, 0.7, 1)
        left_sidebar = core.screen.create_window(0.0, 0.0, 0.15, 1) 
        right_sidebar = core.screen.create_window(0.85, 0.0, 0.15, 1)
        difficulty = 1

        generator = Dungeon_generator(Layout_generator_spanning())
        rooms = generator.generate(main_window, left_sidebar, right_sidebar, difficulty)

        current_room = 0
        Object_storage().clone(rooms[current_room].scene.world, "Player", "Default", [(0.5, 0.5)])

        POS = {
            'U': (0.8, None),
            'D': (0.2, None),
            'R': (None, 0.2),
            'L': (None, 0.8)
        }

        dt = 0 
        running = True
        floor_counter = 1
        while running:
            start = time.time()

            # Executes a frame
            rooms[current_room].scene.event_handler.dispatch_event(evt.Print_event("Floor", floor_counter, right_sidebar))
            ret_lst = rooms[current_room].scene.run(dt)
            r = None
            for ret in ret_lst:
                if ret in "UDRL":
                    rooms[current_room].scene.cleanup()
                    current_room = self._move_players(rooms, current_room, ret)
                if ret == "exit":
                    difficulty += 0.2
                    new_rooms = generator.generate(main_window, left_sidebar, right_sidebar, difficulty)
                    self._clone_players(rooms[current_room], new_rooms[0])
                    current_room = 0
                    rooms = new_rooms
                    floor_counter += 1
                if ret == "Terminate":
                    running = False

            # Calc dt
            stop = time.time()
            dt = stop - start
            time.sleep(max(1 / self.FPS - dt, 0))
            dt = max(dt, 1 / self.FPS)

        del main_window
        del left_sidebar
        del right_sidebar

    def run(self):
        core.screen.wrapper(self._run)