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
dt_lst = []

try:
    dt = 0 
    while True:
        start = time.time()

        scene.run(dt)

        stop = time.time()
        dt = stop - start
        time.sleep(max(1 / 30 - dt, 0))
        dt = max(dt, 1 / 30)
        dt_lst.append(dt)
except:
    f = open("dt_logging.txt", "a")
    for dt in dt_lst:
        f.write(str(dt) + " ")
    f.close()
    core.Screen_wrapper().exit()
    traceback.print_exc()
    print("hello")
