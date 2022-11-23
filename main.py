
import sys

sys.path.insert(1, 'core')
import core
import scene as sc
import time

core.Screen_wrapper().init()
scene = sc.Scene()
dt = 0 
while True:
    start = time.time()

    scene.run(dt)

    stop = time.time()
    dt = stop - start
    time.sleep(max(1 / 60 - dt, 0))
    dt = max(dt, 1 / 60)