import sys

sys.path.insert(1, 'core')
from object_storage import Object_storage
import core
import components as comp
from typing import Callable

# DEBUG
debug = True

def constructor(delegated_constructor: Callable):
    def _(world, components, arguments):
        entity = world.create_entity()
        for component in components:
            entity.add_component(component)
        delegated_constructor(world, entity, arguments)
    return _

# 0: (pos_x, pos_y)
def transform_constructor(world, entity, arguments):
    [comp_tran] = entity.query_components([comp.C_transform])
    comp_tran.x = arguments[0][0]
    comp_tran.y = arguments[0][1]
    comp_tran.last_x = arguments[0][0]
    comp_tran.last_y = arguments[0][1]

# 0: (width, height)
def hitbox_constructor(world, entity, arguments):
    [comp_hitbox] = entity.query_components([comp.C_hitbox])
    comp_hitbox.w = arguments[0][0]
    comp_hitbox.h = arguments[0][1]

# 0: Parent_entity
# 1: (rel_size_w, rel_size_h)
def range_constructor(world, entity, arguments):
    [comp_tran_parent] = arguments[0].query_components([comp.C_transform])
    transform_constructor(world, entity, [(comp_tran_parent.x - arguments[1][0] / 2, comp_tran_parent.y - arguments[1][1] / 2)])
    hitbox_constructor(world, entity, [arguments[1]])

    [comp_range, comp_child] = entity.query_components([comp.C_range, comp.C_child_of])
    comp_child.parent = arguments[0]
    comp_range.offset = (-arguments[1][0] / 2, -arguments[1][1] / 2)
    
    # DEBUG
    if not debug:
        entity.remove_component(comp.C_rectangle)
        return
    [comp_rect] = entity.query_components([comp.C_rectangle])
    comp_rect.width = arguments[1][0]
    comp_rect.height = arguments[1][1]

# 0: (pos_x, pos_y)
def ghost_constructor(world, entity: core.World.Entity_wrapper, arguments):
    global debug
    transform_constructor(world, entity, arguments)
    debug = False 
    Object_storage().clone(world, "Misc", "Range", [entity, (0.3, 0.3)])
    debug = True

# 0: (pos_x, pos_y)
def gangster_constructor(world, entity: core.World.Entity_wrapper, arguments):
    global debug
    transform_constructor(world, entity, arguments)
    debug = False
    Object_storage().clone(world, "Misc", "Range", [entity, (0.75, 0.75)])
    debug = True

# 0: (pos_x, pos_y)
def monkey_constructor(world, entity: core.World.Entity_wrapper, arguments):
    global debug
    debug = False
    transform_constructor(world, entity, arguments)
    Object_storage().clone(world, "Misc", "Range", [entity, (2, 2)])
    debug = True

# 0: dir
# 1: (pos_x, pos_y)
def bullet_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[1]])
    [comp_bullet] = entity.query_components([comp.C_bullet])
    comp_bullet.dir = arguments[0]

# 0: (pos_x, pos_y)
# 1: (width, height)
def dynamic_wall_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    hitbox_constructor(world, entity, [arguments[1]])
    [comp_rectangle] = entity.query_components([comp.C_rectangle])
    comp_rectangle.width = arguments[1][0]
    comp_rectangle.height = arguments[1][1]

# 0: name
# 1: (pos_x, pos_y)
# 2: (width, height)
def exit_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[1]])
    hitbox_constructor(world, entity, [arguments[2]])
    [comp_exit] = entity.query_components([comp.C_exit])
    comp_exit.name = arguments[0]

# 0: (pos_x, pos_y)
# 1: radius
# 2: det_time
def bomb_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    [comp_bomb] = entity.query_components([comp.C_bomb])
    comp_bomb.det_time = arguments[2]
    comp_bomb.radius = arguments[1]

# 0: (pos_x, pos_y)
# 1: radius
def explosion_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    hitbox_constructor(world, entity, [(arguments[1] * 2, arguments[1] * 2)])
    [comp_rect] = entity.query_components([comp.C_rectangle])
    comp_rect.width = arguments[1] * 2
    comp_rect.height = arguments[1] * 2

# 0: (pos_x, pos_y)
def fox_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    Object_storage().clone(world, "Misc", "Range", [entity, (0.5, 0.5)])

# TODO: parse file with the information instead of hardcoding into code
def fill_object_storage():
    Object_storage().add("Misc", "Range", [
        comp.C_range(None),
        comp.C_transform(None, None),
        comp.C_hitbox(None, None, True),
        comp.C_child_of(None),
        comp.C_rectangle(None, None)
    ],constructor(range_constructor))

    Object_storage().add("Player", "Default", [\
        comp.C_player(),\
        comp.C_transform(None, None),\
        comp.C_sprite([" ~~~ ","|0>0|"," \o/ "]),\
        comp.C_hitbox(5, 3),\
        comp.C_health(100)\
    ],constructor(transform_constructor))

    Object_storage().add("Monster", "Ghost", [\
        comp.C_ghost(0.03),\
        comp.C_ai(0.06),\
        comp.C_transform(None, None),\
        comp.C_sprite([" _ ","0 0","~~~"]),\
        comp.C_hitbox(3, 3),\
        comp.C_health(20),\
        comp.C_thorn(1),\
        comp.C_monster()
    ],constructor(ghost_constructor))

    Object_storage().add("Monster", "Gangster", [\
        comp.C_gangster(1),\
        comp.C_ai(0.01),\
        comp.C_transform(None, None),\
        comp.C_sprite(["_-----"," (-#_#)","  --]=="]),\
        comp.C_hitbox(7, 3),\
        comp.C_health(20),\
        comp.C_thorn(1),\
        comp.C_monster()
    ],constructor(gangster_constructor))

    Object_storage().add("Monster", "Monkey", [\
        comp.C_monkey(),\
        comp.C_ai(0.02, ((0.4, 0.4), (0.6, 0.6))),\
        comp.C_transform(None, None),\
        comp.C_sprite([
            "     ,\"^\".     ",
            "    / _=_ \    ",
            "   (,(ovo),)   ",
            " .-.\(-\"-)/.-. ",
            "{    \___/    }",
            "{   } .  . {  }",
            "{   --| |--   }",
            " \____| |____/ ",
            "      | |      "
        ]),\
        comp.C_hitbox(15, 9),\
        comp.C_health(20),\
        comp.C_thorn(1),\
        comp.C_monster()
    ],constructor(monkey_constructor))

    Object_storage().add("Monster", "Boomer", [\
        comp.C_boomer(10),\
        comp.C_ai(0.03),\
        comp.C_transform(None, None),\
        comp.C_health(10),\
        comp.C_sprite([ 
            " _____ ",
            "|O . O|",
            " \[']/",
        ]),\
        comp.C_hitbox(7,3),\
        comp.C_thorn(1),\
        comp.C_monster()
        ],constructor(transform_constructor))

    Object_storage().add("Monster", "Fox", [\
        comp.C_fox(),\
        comp.C_ai(0.05),\
        comp.C_transform(None, None),\
        comp.C_health(10),\
        comp.C_sprite([
            "(\ _ /)",
            "\<> <>/",
            "  \./  "
        ]),\
        comp.C_hitbox(7,3),\
        comp.C_thorn(1),\
        comp.C_monster()
        ],constructor(fox_constructor))

    Object_storage().add("Projectile", "Bomb", [\
        comp.C_transform(None, None),\
        comp.C_sprite([
            "[']"
        ]),\
        comp.C_bomb(10, 10)
    ],constructor(bomb_constructor))

    Object_storage().add("Misc", "Explosion", [\
        comp.C_transform(None, None),\
        comp.C_rectangle(None, None),\
        comp.C_hitbox(None, None, True),\
        comp.C_thorn(1),\
        comp.C_lifetime(10)\
        ],constructor(explosion_constructor))

    Object_storage().add("Projectile", "Bullet",[\
        comp.C_bullet(None, 0.3),\
        comp.C_transform(None, None),\
        comp.C_sprite(["*"]),\
        comp.C_hitbox(1, 1),\
        comp.C_thorn(1)
    ],constructor(bullet_constructor))

    Object_storage().add("Misc", "Sword" [\
        comp.C_transform(None, None),\
        comp.C_enemythorn(1),\
        comp.C_hitbox(),\
        comp.C_animation(),\
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
    ],constructor(dynamic_wall_constructor))

    Object_storage().add("Item", "Text",[
        comp.C_transform(0, 0),
        comp.C_text(None)
    ])

    Object_storage().add("Misc", "Exit",[
        comp.C_transform(None, None),
        comp.C_hitbox(None, None, True),
        comp.C_exit(None)
    ],constructor(exit_constructor))