import curses
import event_handler as es
from numbers import Number
from typing import Tuple
import regex as re

class Key_event(es.Event):
    def __init__(self, key):
        self.key = key

# Represents a window which we can draw to using coordinates between 0 and 1
class Window(): 
    def __init__(self, window):
        self.window = window
        self.children = []
    
    def refresh(self):
        self.window.refresh()
        self.window.clear()
    
    def draw_row(self, row: str, abs_x: int, abs_y: int):
        [max_height, max_width] = self.get_dimension()
        if (abs_x >= max_width or abs_y >= max_height):
            return

        dist_to_right = max_width - abs_x 
        row_split = re.split(r'(!+)', row[min(len(row),max(0, -abs_x)):len(row)])

        for seq in row_split:
            if abs_x >= max_width:
                break
            if len(seq) != 0 and seq[0] != '!':
                self.window.addstr(abs_y, abs_x, seq)
            abs_x += len(seq)

    def draw_texture(self, texture, rel_x, rel_y):
        [abs_x, abs_y] = self.rel_to_abs(rel_x, rel_y)
        for texture_row in texture:
            self.draw_row(texture_row, abs_x, abs_y)
            abs_y += 1
    
    def get_dimension(self) -> list[int, int]:
        return self.window.getmaxyx()

    def rel_to_abs(self, x: Number, y: Number) -> Tuple[int, int]:
        [height, width] = self.get_dimension()
        return (int(x * (width - 1)), int(y * (height - 1)))

    def abs_to_rel(self, x: int, y: int) -> Tuple[Number, Number]:
        [height, width] = self.get_dimension()
        return ((x / (width - 1)), (y / (height - 1)))

    def create_window(self, rel_x, rel_y, rel_width, rel_height):
        [abs_x, abs_y] = self.rel_to_abs(rel_x, rel_y)
        [abs_width, abs_height] = self.rel_to_abs(rel_width, rel_height)
        child_window = Window(self.window.derwin(abs_height, abs_width, abs_y, abs_x))
        self.children.append((child_window, (rel_x, rel_y, rel_width, rel_height)))
        return child_window
    
    def _resize(self, abs_x: int, abs_y: int, abs_width: int, abs_height: int):
        # TODO: reinit each window / reconstruct / create a new window with the correct dimensions. This is slower? but this shouldn't matter
        self.window.resize(1, 1) # otherwise mvwin will move the window out of bounds which will make the program crash
        self.window.mvwin(abs_y, abs_x)
        self.window.resize(abs_height, abs_width)
        for child in self.children:
            child[0]._resize(int(child[1][0] * abs_width), int(child[1][1] * abs_height), int(child[1][2] * abs_width), int(child[1][3] * abs_height))

    def draw_rectangle(self, rel_x: Number, rel_y: Number, rel_width: Number, rel_height: Number):
        [abs_x, abs_y] = self.rel_to_abs(rel_x, rel_y) 
        [abs_width, abs_height] = self.rel_to_abs(rel_width, rel_height) 
        top = abs_y + abs_height
        self.draw_row("#"*abs_width, abs_x, abs_y)
        while abs_y < top:
            self.draw_row("#", abs_x, abs_y)
            self.draw_row("#", abs_x + abs_width, abs_y)
            abs_y += 1
        self.draw_row("#"*abs_width, abs_x, top)

    def draw_text(self, rel_x: Number, rel_y: Number, text: str):
        [abs_x, abs_y] = self.rel_to_abs(rel_x, rel_y) 
        self.draw_row(text, abs_x, abs_y)

# Is the main windows which all the other windows will be children of
class Screen(Window):
    def _wrapper(self, stdscr, func):
        curses.curs_set(0)
        self.stdscr = stdscr
        self.window = stdscr
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        func()
        self.stdscr = None

    def wrapper(self, func):
        curses.wrapper(self._wrapper, func)

    def __init__(self):
        self.stdscr = None
        super().__init__(self.stdscr)

    def poll_events(self, event_handler: es.Event_handler):
        keypress = self.window.getch()
        if keypress == curses.KEY_RESIZE:
            [height, width] = self.get_dimension()
            self._resize(0, 0, width, height)
            self.refresh()
        if keypress != -1:
            event_handler.dispatch_event(Key_event(keypress))

screen = Screen()