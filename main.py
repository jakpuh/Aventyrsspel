import sys

sys.path.insert(1, 'core')
import core
import scene as sc
import time
import traceback
import object_storage_builder as storage_builder

core.Screen_wrapper().init()
storage_builder.fill_object_storage()

scene = sc.Scene()

try:
    dt = 0 
    while True:
        start = time.time()

        scene.run(dt)

        stop = time.time()
        dt = stop - start
        time.sleep(max(1 / 60 - dt, 0))
        dt = max(dt, 1 / 60)
except Exception:
    core.Screen_wrapper().exit()
    traceback.print_exc()
