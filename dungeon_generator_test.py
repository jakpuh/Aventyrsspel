from dungeon_generator import *
from dungeon_generator_algorithm import *
import sys

sys.path.insert(1, 'core')
import core
import scene as sc
import time
import traceback
import object_storage_builder as storage_builder

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
                current_room = rooms[current_room].neighbours[ret]

        stop = time.time()
        dt = stop - start
        time.sleep(max(1 / FPS - dt, 0))
        dt = max(dt, 1 / FPS)
except:
    core.Screen_wrapper().exit()
    traceback.print_exc()
