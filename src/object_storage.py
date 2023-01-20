import core.core as core
import copy
from typing import Callable

# Prototype pattern: https://en.wikipedia.org/wiki/Prototype_pattern
class Object_storage(metaclass=core.Singleton):
    def __init__(self):
        self.objects = {} 

    # Adds an objects which can be cloned
    def add(self, obj_class: str, obj_name: str, components: list[core.Component], constructor: Callable = None):
        if not obj_class in self.objects:
            self.objects[obj_class] = {}
        if obj_name in self.objects[obj_class]:
            raise Exception("Object already in system")
        self.objects[obj_class][obj_name] = (copy.deepcopy(components), constructor)
    
    # Clones the specified object into the world and returns it
    def clone(self, world, obj_class: str, obj_name: str, arguments: list = None) -> list[core.Component]:
        if not obj_class in self.objects:
            raise Exception("Object class not found")
        if not obj_name in self.objects[obj_class]:
            raise Exception("Object not found in class")
        comp_copy = copy.deepcopy(self.objects[obj_class][obj_name][0])
        return self.objects[obj_class][obj_name][1](world, comp_copy, arguments)
