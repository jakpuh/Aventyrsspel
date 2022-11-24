import curses
import event_system as es
import singleton

class Key_event(es.Event):
    def __init__(self, key):
        self.key = key
       
class Screen_wrapper(metaclass=singleton.Singleton):
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
        [abs_x, abs_y] = self.rel_to_abs(rel_x, rel_y)
        for texture_row in texture:
            self.stdscr.addstr(abs_y, abs_x, texture_row)
            abs_y += 1

    def get_dimension(self):
        return self.stdscr.getmaxyx()

    def rel_to_abs(self, x, y):
        [height, width] = self.get_dimension()
        return [int(x * (width - 2)), int(y * (height - 2))]

    def poll_events(self, event_handler):
        keypress = self.stdscr.getch()
        if keypress != -1:
            event_handler.dispatch_event(Key_event(keypress))