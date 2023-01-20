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
import components.components as comp
import curses
import time
import events as evt
import game_manager as GM

GM.Game_manager().run()