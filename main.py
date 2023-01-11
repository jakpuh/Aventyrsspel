from dungeon_generator import *
from dungeon_generator_algorithm import *
import sys

sys.path.insert(1, 'core')
import core
import scene as sc
import time
import traceback
import object_storage_builder as storage_builder
from object_storage import *
import components as comp
import curses
import time

FPS = 30


def main():
    last_dirs = [1,2,3,4]

    main_window = core.screen.create_window(0.15, 0, 0.7, 1)
    left_sidebar = core.screen.create_window(0.0, 0.0, 0.15, 1) 
    right_sidebar = core.screen.create_window(0.85, 0.0, 0.15, 1)
    # left_sidebar = core.screen.create_window(0.9, 0.0, 0.1, 1)
    storage_builder.fill_object_storage()

    generator = Dungeon_generator(Layout_generator_spanning())
    # rooms = generator.generate(core.screen, core.screen, core.screen)
    rooms = generator.generate(main_window, left_sidebar, right_sidebar)
    # rooms = generator.generate(main_window, right_sidebar)

    current_room = 0
    Object_storage().clone(rooms[current_room].scene.world, "Player", "Default", [(0.5, 0.5)])

    POS = {
        'U': (0.8, None),
        'D': (0.2, None),
        'R': (None, 0.2),
        'L': (None, 0.8)
    }

    dt = 0 
    while True:
        start = time.time()

        # scene.run(dt)
        ret_lst = rooms[current_room].scene.run(dt)
        # print(last_dirs)
        for ret in ret_lst:
            if ret in "UDRL":
                rooms[current_room].scene.cleanup()
                last_dirs = last_dirs[1:]
                last_dirs.append(ret)
                next_room = rooms[current_room].neighbours[ret]
                player_entities = rooms[current_room].scene.world.get_entities([comp.C_player])
                for player in player_entities:
                    player_components = player.query_components_all()
                    new_player = rooms[next_room].scene.world.create_entity()
                    for player_component in player_components:
                        new_player.add_component(player_component)
                    [tran_comp] = new_player.query_components([comp.C_transform])
                    tran_comp.y = POS[ret][0] if POS[ret][0] != None else tran_comp.y
                    tran_comp.x = POS[ret][1] if POS[ret][1] != None else tran_comp.x
                    tran_comp.last_y = POS[ret][0] if POS[ret][0] != None else tran_comp.y
                    tran_comp.last_x = POS[ret][1] if POS[ret][1] != None else tran_comp.x
                    player.destroy_entity()
                current_room = next_room

        stop = time.time()
        dt = stop - start
        # time.sleep(max(1 / FPS - dt, 0))
        time.sleep(max(1 / FPS - dt, 0))
        # curses.napms(int(max(1 / FPS - dt, 0)) * 1000)
        dt = max(dt, 1 / FPS)

core.screen.wrapper(main)