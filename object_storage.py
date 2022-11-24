import sys

sys.path.insert(1, 'core')
import core

class Object_storage(metaclass=core.Singleton):
    def __init__(self):
        self.objects = {} 

    def add(self, obj_class: str, obj_name: str, components: list[core.Component]):
        if not obj_class in self.objects:
            self.objects[obj_class] = {}
        if obj_name in self.objects[obj_class]:
            raise Exception("Object already in system")
        self.objects[obj_class][obj_name] = components
    
    def get(self, obj_class: str, obj_name: str) -> list[core.Component]:
        if not obj_class in self.objects:
            raise Exception("Object class not found")
        if not obj_name in self.objects[obj_class]:
            raise Exception("Object not found in class")
        return self.objects[obj_class][obj_name]
