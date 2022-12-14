import curses
import event_system as es
import singleton

class Key_event(es.Event):
    def __init__(self, key):
        self.key = key
       
class Screen_wrapper(metaclass=singleton.Singleton):
    '''
    Singleton class which represents the console which the user is playing on.
    '''
    stdscr = None

    def init(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

    def refresh(self):
        self.stdscr.refresh()
        self.stdscr.clear()

    def exit(self):
        curses.nocbreak()
        curses.curs_set(0)
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def draw_row(self, row, abs_x, abs_y):
        [max_height, max_width] = self.get_dimension()
        if (abs_x >= max_width or abs_y >= max_height):
            return
        dist_to_right = max_width - abs_x 
        self.stdscr.addstr(max(abs_y, 0), max(abs_x, 0), row[0:min(len(row), dist_to_right)])

    def draw_texture(self, texture, rel_x, rel_y):
        [abs_x, abs_y] = self.rel_to_abs(rel_x, rel_y)
        for texture_row in texture:
            self.draw_row(texture_row, abs_x, abs_y)
            abs_y += 1

    def get_dimension(self):
        return self.stdscr.getmaxyx()

    def rel_to_abs(self, x, y):
        [height, width] = self.get_dimension()
        return [int(x * (width - 2)), int(y * (height - 2))]

    def abs_to_rel(self, x, y):
        [height, width] = self.get_dimension()
        ##return [int(x * (width - 2)), int(y * (height - 2))]

    def abs_to_rel(self, x, y):
        [height, width] = self.get_dimension()
        return [(x / (width - 2)), (y / (height - 2))]

    def poll_events(self, event_handler):
        keypress = self.stdscr.getch()
        if keypress != -1:
            event_handler.dispatch_event(Key_event(keypress))
    
# ================== DEBUG ===================0
    def draw_rectangle(self, rel_x, rel_y, rel_width, rel_height):
        [max_height, max_width] = self.get_dimension()
        [abs_x, abs_y] = self.rel_to_abs(rel_x, rel_y) 
        [abs_width, abs_height] = self.rel_to_abs(rel_width, rel_height) 
        top = abs_y + abs_height
        self.draw_row("#"*abs_width, abs_x, abs_y)
        while abs_y < top:
            self.draw_row("#", abs_x, abs_y)
            self.draw_row("#", abs_x + abs_width, abs_y)
            abs_y += 1
        self.draw_row("#"*abs_width, abs_x, top)
