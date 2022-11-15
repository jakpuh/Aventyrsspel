import curses
import event_system as es

class Key_event(es.Event):
    def __init__(self, key):
        self.key = key

# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class Screen_wrapper(metaclass=Singleton):
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
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def draw_texture(self, texture, rel_x, rel_y):
        height, width = self.stdscr.getmaxyx()
        abs_y = int(rel_y * height)
        abs_x = int(rel_x * width)
        for texture_row in texture:
            self.stdscr.addstr(abs_y, abs_x, texture_row)
            abs_y += 1

    def get_dimension(self):
        return self.stdscr.getmaxyx()

    def rel_to_abs(self, x, y):
        [height, width] = self.get_dimension()
        return [int(x * (width - 1)), int(y * (height - 1))]

    def poll_events(self, event_handler):
        keypress = self.stdscr.getch()
        if keypress != -1:
            event_handler.dispatch_event(Key_event(keypress))