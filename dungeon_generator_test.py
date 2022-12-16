from dungeon_generator import *
from dungeon_generator_algorithm import *
import sys

sys.path.insert(1, 'core')
import core
import scene as sc
import time
import traceback
import object_storage_builder as storage_builder
import components as comp

FPS = 30

core.Screen_wrapper().init()
storage_builder.fill_object_storage()

scene = sc.Scene(['U'])

generator = Dungeon_generator(Layout_generator_spanning())
rooms = generator.generate()

current_room = 0
try:
    dt = 0 
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
                    player.destroy_entity()
                current_room = next_room

        stop = time.time()
        dt = stop - start
        time.sleep(max(1 / FPS - dt, 0))
        dt = max(dt, 1 / FPS)
except:
    core.Screen_wrapper().exit()
    traceback.print_exc()
