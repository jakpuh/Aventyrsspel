# TODO: should delegate the responsibility of difficulty handling to another module
'''
Handles the constructor of the different pre built entities
This makes it less complex for the game to create entities
'''
import core.core as core
from object_storage import Object_storage
import components.components as comp
from typing import Callable

# DEBUG
debug = False

# Creates an entity and 
# returns a constructor which will be called when the entity gets created
def constructor(delegated_constructor: Callable):
    def _(world, components, arguments):
        entity = world.create_entity()
        for component in components:
            entity.add_component(component)
        delegated_constructor(world, entity, arguments)
        return entity
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

# 0: Parent entity
def child_constructor(world, entity, arguments):
    [comp_child] = entity.query_components([comp.C_child_of])
    comp_child.parent = arguments[0] 
    components = arguments[0].query_components([comp.C_friend, comp.C_enemy])
    for component in components:
        entity.add_component(component)

# 0: Parent entity
# 1: (rel_size_w, rel_size_h)
def range_constructor(world, entity, arguments):
    [comp_tran_parent] = arguments[0].query_components([comp.C_transform])
    transform_constructor(world, entity, [(comp_tran_parent.x - arguments[1][0] / 2, comp_tran_parent.y - arguments[1][1] / 2)])
    hitbox_constructor(world, entity, [arguments[1]])
    child_constructor(world, entity, [arguments[0]])

    [comp_follow] = entity.query_components([comp.C_follow])
    comp_follow.offset = (-arguments[1][0] / 2, -arguments[1][1] / 2)
    
    # DEBUG
    if not debug:
        entity.remove_component(comp.C_rectangle)
        return
    [comp_rect] = entity.query_components([comp.C_rectangle])
    comp_rect.width = arguments[1][0]
    comp_rect.height = arguments[1][1]

# 0: (pos_x, pos_y)
# 1: difficulty
def ghost_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, arguments)
    [comp_thorn, comp_ghost] = entity.query_components([comp.C_thorn, comp.C_ghost])
    comp_thorn.damage *= arguments[1]
    comp_ghost.speed = min(comp_ghost.speed * arguments[1], 0.4)
    Object_storage().clone(world, "Misc", "Range", [entity, (0.3, 0.3)])

# 0: (pos_x, pos_y)
# 1: difficulty
def gangster_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, arguments)
    [comp_thorn, comp_shoot] = entity.query_components([comp.C_thorn, comp.C_shoot])
    comp_thorn.damage *= arguments[1]
    comp_shoot.fire_rate = int(comp_shoot.fire_rate * (1 / arguments[1]) ** 0.5)
    comp_shoot.burst_size = int(2 * arguments[1] - 1)

    Object_storage().clone(world, "Misc", "Range", [entity, (0.75, 0.75)])

# 0: (pos_x, pos_y)
# 1: difficulty
def monkey_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, arguments)
    [comp_thorn, comp_shoot, comp_dash, comp_throw] = entity.query_components([comp.C_thorn, comp.C_shoot, comp.C_dash, comp.C_throw_bombs])
    comp_thorn.damage *= arguments[1]
    comp_shoot.fire_rate = int(comp_shoot.fire_rate * (1 / arguments[1]) ** 0.5)
    comp_shoot.burst_size = int(2 * arguments[1] - 1)
    comp_dash.speed = min(comp_dash.speed * arguments[1], 1)
    comp_throw.fire_rate = int(comp_throw.fire_rate * (1 / arguments[1]) ** 0.5)
    Object_storage().clone(world, "Misc", "Range", [entity, (2, 2)])
    entity.disable_components([comp.C_dash])
    entity.disable_components([comp.C_shoot])
    entity.disable_components([comp.C_throw_bombs])

# 0: dir
# 1: (pos_x, pos_y)
# 2: difficulty
def bullet_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[1]])
    [comp_bullet] = entity.query_components([comp.C_bullet])
    comp_bullet.dir = arguments[0]
    comp_bullet.speed = min(comp_bullet.speed * arguments[2], 0.3)

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
# 3: difficulty
def bomb_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    [comp_bomb] = entity.query_components([comp.C_bomb])
    comp_bomb.det_time = arguments[2]
    comp_bomb.radius = arguments[1]

# 0: (pos_x, pos_y)
# 1: radius
# 2: difficulty 
def explosion_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    hitbox_constructor(world, entity, [(arguments[1] * 2, arguments[1] * 2)])
    [comp_rect, comp_thorn] = entity.query_components([comp.C_rectangle, comp.C_thorn])
    comp_thorn.damage *= arguments[2]
    comp_rect.width = arguments[1] * 2
    comp_rect.height = arguments[1] * 2

# 0: (pos_x, pos_y)
# 1: difficulty
def fox_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    [comp_dash, comp_thorn] = entity.query_components([comp.C_dash, comp.C_thorn])
    comp_dash.speed = min(comp_dash.speed * arguments[1], 0.5)
    comp_thorn.damage *= arguments[1]
    Object_storage().clone(world, "Misc", "Range", [entity, (0.7, 0.7)])
    entity.disable_components([comp.C_dash])

# 0: Parent entity
# 1: Damage
def spinning_swords_constructor(world, entity: core.World.Entity_wrapper, arguments):
    child_constructor(world, entity, [arguments[0]])
    [comp_thorn] = entity.query_components([comp.C_thorn])
    comp_thorn.damage = arguments[1]

# 0: action
# TODO: pus constructor as prefix instead of suffix
def game_manager_boss_constructor(world, entity: core.World.Entity_wrapper, arguments):
    [comp_gm_boss] = entity.query_components([comp.C_boss_game_manager])
    comp_gm_boss.action = arguments[0]

# 0: (pos_x, pos_y)
# 1: health
# 2: damage
# 3: speed
def chest_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    [comp_chest] = entity.query_components([comp.C_chest])
    comp_chest.health = arguments[1]
    comp_chest.damage = arguments[2]
    comp_chest.speed  = arguments[3]

# 0: (pos_x, pos_y)
# 1: difficulty
def boomer_constructor(world, entity: core.World.Entity_wrapper, arguments):
    transform_constructor(world, entity, [arguments[0]])
    [comp_throw] = entity.query_components([comp.C_throw_bombs])
    comp_throw.fire_rate = int(comp_throw.fire_rate * (1 / arguments[1]))

# TODO: parse file with the information instead of hardcoding into code
def fill_object_storage():
    Object_storage().add("GameManager", "Boss", [
        comp.C_boss_game_manager(None)
    ],constructor(game_manager_boss_constructor))

    Object_storage().add("Misc", "Range", [
        comp.C_scout(),
        comp.C_transform(None, None),
        comp.C_hitbox(None, None, True),
        comp.C_child_of(None),
        comp.C_follow(None, True),
        comp.C_rectangle(None, None)
    ],constructor(range_constructor))

    Object_storage().add("Player", "Default", [\
        comp.C_player(0.02, 1),
        comp.C_friend(), 
        comp.C_transform(None, None),\
        comp.C_sprite([
            "!~~~",
            "|0>0|",
            "!\o/"
        ]),\
        comp.C_hitbox(5, 3),\
        comp.C_health(10),
        comp.C_xp(0) 
    ],constructor(transform_constructor))

    Object_storage().add("Monster", "Ghost", [\
        comp.C_ghost(0.03),\
        comp.C_ai(0.06),\
        comp.C_enemy(),
        comp.C_delay(),
        comp.C_transform(None, None),\
        comp.C_sprite([
            "!_!",
            "0 0",
            "~~~"
        ]),\
        comp.C_hitbox(3, 3),\
        comp.C_health(6),\
        comp.C_thorn(1),\
        comp.C_xp(20) 
    ],constructor(ghost_constructor))

    Object_storage().add("Monster", "Gangster", [\
        comp.C_gangster(),\
        comp.C_shoot(20, 1),
        comp.C_ai(0.01),\
        comp.C_enemy(),
        comp.C_delay(),
        comp.C_transform(None, None),\
        comp.C_sprite([
            "_-----",
            "!(-#_#)",
            "!!--]=="
        ]),\
        comp.C_hitbox(7, 3),\
        comp.C_health(3),\
        comp.C_thorn(1),\
        comp.C_xp(30) 
    ],constructor(gangster_constructor))

    Object_storage().add("Monster", "Monkey", [\
        comp.C_monkey(),\
        comp.C_enemy(),
        comp.C_transform(None, None),\
        comp.C_xp(100),
        comp.C_delay(),
        comp.C_ai(0.02, ((0.4, 0.4), (0.6, 0.6))),
        comp.C_dash(0.4, 5),
        comp.C_normal_trigger(-15),
        comp.C_throw_bombs(9),
        comp.C_shoot(9, 3),
        comp.C_sprite([
            "!!!!!,\"^\".",
            "!!!!/ _=_ \\",
            "!!!(,(ovo),)",
            "!.-.\(-\"-)/.-.",
            "{    \___/    }",
            "{   } .  . {  }",
            "{   --| |--   }",
            "!\____| |____/",
            "!!!!!!| |"
        ]),\
        comp.C_hitbox(15, 9),\
        comp.C_health(20),\
        comp.C_thorn(1),\
    ],constructor(monkey_constructor))

    Object_storage().add("Monster", "Boomer", [\
        comp.C_ai(0.03),
        comp.C_enemy(),
        comp.C_delay(),
        comp.C_throw_bombs(10),
        comp.C_transform(None, None),\
        comp.C_health(6),\
        comp.C_xp(25),
        comp.C_sprite([ 
            "!_____",
            "|O . O|",
            "!\[']/",
        ]),\
        comp.C_hitbox(7,3),\
        comp.C_thorn(1),\
        ],constructor(boomer_constructor))

    Object_storage().add("Monster", "Fox", [\
        comp.C_dasher(),
        comp.C_dash(0.3),
        comp.C_normal_trigger(0),
        comp.C_ai(0.05),\
        comp.C_enemy(),
        comp.C_transform(None, None),\
        comp.C_health(5),\
        comp.C_sprite([
            "(\ _ /)",
            "\<> <>/",
            "!!\./"
        ]),\
        comp.C_delay(),
        comp.C_hitbox(7,3),\
        comp.C_xp(10),
        comp.C_thorn(1),\
    ],constructor(fox_constructor))

    Object_storage().add("Misc", "Chest", [\
        comp.C_chest(None, None, None),\
        comp.C_transform(None, None),\
        comp.C_sprite(["!!!__----__",
                        "!/          \\",
                        "|-----O------|",
                        "|            |",
                        "|____________|"]),\
        comp.C_hitbox(14, 5),\
    ],constructor(chest_constructor))

    Object_storage().add("Projectile", "Bomb", [\
        comp.C_transform(None, None),\
        comp.C_sprite([
            "[']"
        ]),\
        comp.C_bomb(10, 7)
    ],constructor(bomb_constructor))

    Object_storage().add("Misc", "Explosion", [\
        comp.C_transform(None, None),\
        comp.C_rectangle(None, None),\
        comp.C_hitbox(None, None, True),\
        comp.C_thorn(1),\
        comp.C_enemy(),
        comp.C_lifetime(7)\
        ],constructor(explosion_constructor))

    Object_storage().add("Projectile", "Bullet",[\
        comp.C_bullet(None, 0.3),\
        comp.C_transform(None, None),\
        comp.C_sprite(["*"]),\
        comp.C_enemy(),
        comp.C_hitbox(1, 1),\
        comp.C_thorn(1)
    ],constructor(bullet_constructor))

    Object_storage().add("Misc", "Spinning-swords",[
        comp.C_transform(None, None),
        comp.C_hitbox(15, 13),
        comp.C_follow((-5, -5)),
        comp.C_thorn(None, 11),
        comp.C_friend(),
        comp.C_child_of(None),
        comp.C_sprite(None),
        comp.C_animation([[
            "",
            "",
            "!!!!!!!!!!#",
            "!!!!!!!!!!!#",
            "!###!!!!!!!#",
            "!!!!#!!!!!#",
            "!!!!!!!!!!",
            "!!!!#!!!!!#",
            "!!!#!!!!!!!###",
            "!!!#",
            "!!!!#",
            "",
            ""
            ],[
            "",
            "",
            "!!!!!!!!!!!!!#",
            "!##!!!!!!!!!!#",
            "!!!##!!!!!!!#",
            "!!!!#!!!!!##",
            "!!!!!!!!!!",
            "!!!##!!!!!#",
            "!!!#!!!!!!##",
            "!!#!!!!!!!!!##",
            "!#",
            "",
            ""
            ],[
            "",
            "",
            "",
            "!!###",
            "!!!!!#!!!!!!#",
            "!!!!!!!!!!!!#",
            "!!!##!!!!!##",
            "!!#!!!!!!",
            "!!#!!!!!#",
            "!!!!!!!!!###",
            "",
            "",
            ""
            ],[
            "",
            "",
            "!!!##",
            "!!!!!##",
            "!!!!!!#!!!!!!#",
            "!!!!!!!!!!!!#",
            "!!!##!!!!!##",
            "!!#!!!!!!",
            "!#!!!!!#",
            "!!!!!!!##",
            "!!!!!!!!!##",
            "",
            ""
            ],[
            "",
            "",
            "!!!!!##",
            "!!!!!!!#",
            "!!!!!!!#",
            "!!!!!!!!!!!!!#",
            "!!###!!!!!###",
            "!#!!!!!!!",
            "!!!!!!!#",
            "!!!!!!!#",
            "!!!!!!!!##",
            "",
            ""
            ],[
            "",
            "",
            "!!!!!!##",
            "!!!!!!!!#",
            "!!!!!!!!#",
            "!!###!!!!",
            "!#!!!!!!!!!!!#",
            "!!!!!!!!!!###",
            "!!!!!!#",
            "!!!!!!#",
            "!!!!!!!##"
            "",
            "",
            ],[
            "",
            "!!!!!!!!!!!#",
            "!!!!!!!!!!!#",
            "!!!!!!!!!!#",
            "!##!!!!!!##",
            "!!!##!!!!",
            "!!!!!!!!!!!!##",
            "!!!!!!!!!!##",
            "!!!!##",
            "!!!!#",
            "!!!#",
            "!!!#"
            "",
            ],[
            "",
            "",
            "!!!!!!!!!!#",
            "!!!!!!!!!!!#",
            "!###!!!!!!!#",
            "!!!!#!!!!!#",
            "!!!!!!!!!",
            "!!!!#!!!!!#",
            "!!!#!!!!!!!###",
            "!!!#",
            "!!!!#",
            "",
            ""
            ],[
            "",
            "",
            "!!!!!!!!!!!!!#",
            "!##!!!!!!!!!!#",
            "!!!##!!!!!!!#",
            "!!!!#!!!!!##",
            "!!!!!!!!!!",
            "!!!##!!!!!#",
            "!!!#!!!!!!##",
            "!!#!!!!!!!!!##",
            "!!#",
            "",
            ""
            ]
        ])
    ],constructor(spinning_swords_constructor))

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