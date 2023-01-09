import sys

sys.path.insert(1, 'core')
import core
import copy
from typing import Callable

class Object_storage(metaclass=core.Singleton):
    def __init__(self):
        self.objects = {} 

    def add(self, obj_class: str, obj_name: str, components: list[core.Component], constructor: Callable = None):
        if not obj_class in self.objects:
            self.objects[obj_class] = {}
        if obj_name in self.objects[obj_class]:
            raise Exception("Object already in system")
        self.objects[obj_class][obj_name] = (copy.deepcopy(components), constructor)
    
    def get(self, obj_class: str, obj_name: str) -> list[core.Component]:
        if not obj_class in self.objects:
            raise Exception("Object class not found")
        if not obj_name in self.objects[obj_class]:
            raise Exception("Object not found in class")
        return copy.deepcopy(self.objects[obj_class][obj_name][0])

    def clone(self, world, obj_class: str, obj_name: str, arguments: list = None) -> list[core.Component]:
        if not obj_class in self.objects:
            raise Exception("Object class not found")
        if not obj_name in self.objects[obj_class]:
            raise Exception("Object not found in class")
        comp_copy = copy.deepcopy(self.objects[obj_class][obj_name][0])
        if self.objects[obj_class][obj_name][1] != None:
            self.objects[obj_class][obj_name][1](world, comp_copy, arguments)
