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

try:
    dt = 0 
    while True:
        start = time.time()

        #scene.run(dt)
        rooms[3].scene.run(dt)

        stop = time.time()
        dt = stop - start
        time.sleep(max(1 / FPS - dt, 0))
        dt = max(dt, 1 / FPS)
except:
    core.Screen_wrapper().exit()
    traceback.print_exc()
