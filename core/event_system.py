class Event():
    pass

# TODO: switch name so that it doesn't get confused with a system in ecs
class Event_system():
    def __init__(self):
        self.subscribers = []

    def dispatch_event(self, event):
        for current_event,current_callback in self.subscribers:
            compatible_event = True
            if type(event) != type(current_event):
                continue
            for attribute in vars(current_event):
                if vars(current_event)[attribute] == None:
                    continue
                if not attribute in vars(event) or vars(current_event)[attribute] != vars(event)[attribute]:
                    compatible_event = False
                    break
            if compatible_event:
                current_callback(event)

    def subscribe_event(self, event, callback):
        self.subscribers.append((event, callback))