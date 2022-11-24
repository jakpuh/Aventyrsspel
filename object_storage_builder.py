import sys

sys.path.insert(1, 'core')
from object_storage import Object_storage
import core
import components as comp


# TODO: parse file with the information instead of hardcoding into code
def fill_object_storage():
    Object_storage().add("Player", "Default", [\
        comp.C_player(),\
        comp.C_transform(None, None),\
        comp.C_sprite([" ~~~ ","|0>0|"," \o/ "]),\
        comp.C_hitbox(5, 3),\
        comp.C_health(100)\
    ])
    Object_storage().add("Monster", "Ghost", [\
        comp.C_ghost(2),\
        comp.C_transform(None, None),\
        comp.C_sprite([" _ ","0 0","~~~"]),\
        comp.C_hitbox(3, 3),\
        comp.C_health(20)\
    ])
