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
    main_window = core.screen.create_window(0.4, 0, 0.2, 1)
    #left_sidebar = core.screen.create_window(0.0, 0.0, 0.1, 1) 
    # right_sidebar = core.screen.create_window(0.9, 0.0, 0.1, 1)
    # left_sidebar = core.screen.create_window(0.9, 0.0, 0.1, 1)
    storage_builder.fill_object_storage()

    generator = Dungeon_generator(Layout_generator_spanning())
    # rooms = generator.generate(core.screen, core.screen, core.screen)
    rooms = generator.generate(main_window, main_window, main_window)
    # rooms = generator.generate(main_window, right_sidebar)

    current_room = 0
    player1 = rooms[current_room].scene.world.create_entity()
    player1_components = Object_storage().get("Player", "Default")
    for component in player1_components:
        player1.add_component(component)
    [tran_comp] = player1.query_components([comp.C_transform])
    tran_comp.x = 0.5
    tran_comp.y = 0.5
    tran_comp.last_x = 0.5
    tran_comp.last_y = 0.5

    POS = {
        'U': (0.8, None),
        'D': (0.2, None),
        'R': (None, 0.2),
        'L': (None, 0.8)
    }

    dt = 0 
    try:
        while True:
            start = time.time()

            # scene.run(dt)
            ret_lst = rooms[current_room].scene.run(dt)
            for ret in ret_lst:
                if ret in "UDRL":
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
    except:
        traceback.print_exc()

core.screen.wrapper(main)