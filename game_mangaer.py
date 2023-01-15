import core.core as core
import object_storage_builder as storage_builder
from dungeon_generator import *
from dungeon_generator_algorithm import *

class Game_manager(core.Singleton):
    '''
    Game_manager is a global singleton class which has the responsibility to control the high level aspects of the games loop.
    '''
    def __init__(self):
        '''
        Init inits stuff which only should be initialized once per the lifetime of the application
        '''
        storage_builder.fill_object_storage()
        
    def run(self, layout_generator = Layout_generator_spanning, fps = 30):
        main_window = core.screen.create_window(0.15, 0, 0.7, 1) 
        left_sidebar = core.screen.create_window(0.15, 0, 0.7, 1) 
        right_sidebar = core.screen.create_window(0.15, 0, 0.7, 1) 
        generator = Dungeon_generator(layout_generator())

        rooms = generator.generate(main_window, left_sidebar, right_sidebar)
        current_room = 0
        storage_builder().clone(rooms[current_room].scene.world, "Player", "Default", [(0.5, 0.5)])

        del self.main_window
        del self.left_sidebar
        del self.right_sidebar
        
