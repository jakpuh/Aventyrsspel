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
        comp.C_ghost(0.03),\
        comp.C_ai(0.06),\
        comp.C_transform(None, None),\
        comp.C_sprite([" _ ","0 0","~~~"]),\
        comp.C_hitbox(3, 3),\
        comp.C_health(20),\
        comp.C_thorn(1)\
    ])

    Object_storage().add("Monster", "Gangster", [\
        comp.C_gangster(1),\
        comp.C_ai(0.01),\
        comp.C_transform(None, None),\
        comp.C_sprite(["_-----"," (-#_#)","  --]=="]),\
        comp.C_hitbox(7, 3),\
        comp.C_health(20),\
        comp.C_thorn(1)\
    ])

    Object_storage().add("Projectile", "Bullet",[\
        comp.C_bullet(None, 0.3),\
        comp.C_transform(None, None),\
        comp.C_sprite(["*"]),\
        comp.C_hitbox(1, 1),\
        comp.C_thorn(1)
    ])

    Object_storage().add("Wall", "Default",[\
        comp.C_transform(None, None),\
        comp.C_impenetrable(),\
        comp.C_hitbox(4, 4),\
        comp.C_sprite(["####","####","####","####"])
    ])

    Object_storage().add("Wall", "Dynamic",[
        comp.C_transform(None, None),
        comp.C_impenetrable(),
        comp.C_hitbox(None, None, True),
        comp.C_rectangle(None, None)
        #comp.C_sprite(["####","####","####","####"])
    ])

    Object_storage().add("Item", "Text",[
        comp.C_transform(0, 0),
        comp.C_text(None)
    ])