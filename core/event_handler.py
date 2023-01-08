from typing import Callable

class Event():
    pass

class Event_handler():
    def __init__(self):
        self.subscribers = []

    def dispatch_event(self, event):
        for current_event_type,current_callback,pred in self.subscribers:
            if type(event) != current_event_type:
                continue
            if pred != None and not pred(event):
                continue
            current_callback(event)

    def subscribe_event(self, event_type, callback: Callable[[Event],any], pred: Callable[[Event], bool] = None):
        self.subscribers.append((event_type, callback, pred))