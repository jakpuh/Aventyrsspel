import sys

sys.path.insert(1, 'core')
import ecs


class C_transform(ecs.Component):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
class C_move(ecs.Component):
    def __init__(self, velocity):
        self.velocity = velocity

class Move_system(ecs.System):
    component_mask = [C_transform, C_move]

    def run(self, dt):
        for entity in self.registered_entities:
            [tran_comp, move_comp] = entity.query_components([C_transform, C_move])
            tran_comp.x += move_comp.velocity * dt
            tran_comp.y += move_comp.velocity * dt

world = ecs.World()
world.add_system(Move_system())

entity = world.create_entity()
# add component
component_trans = entity.add_component(C_transform(1, 2))
assert component_trans.x == 1 and component_trans.y == 2 
world.run(1)
assert component_trans.x == 1 and component_trans.y == 2
# add component
component_move = entity.add_component(C_move(3))
assert component_trans.x == 1 and component_trans.y == 2 and component_move.velocity == 3
world.run(1)
assert component_trans.x == 4 and component_trans.y == 5 and component_move.velocity == 3
world.run(1)
assert component_trans.x == 7 and component_trans.y == 8 and component_move.velocity == 3
# query
assert entity.query_components([C_move, C_transform]) == [component_move, component_trans]
# remove component
entity.remove_component(C_move)
# remove component
entity.remove_component(C_move)
# query
assert entity.query_components([C_move, C_transform]) == [component_trans]
world.run(1)
assert component_trans.x == 7 and component_trans.y == 8 
# add component
component_move = entity.add_component(C_move(5))
world.run(1)
assert component_trans.x == 12 and component_trans.y == 13 and component_move.velocity == 5
world.remove_system(Move_system)
world.run(1)
assert component_trans.x == 12 and component_trans.y == 13 and component_move.velocity == 5
entity.destroy_entity()
try: 
    entity.add_component(C_transform(3, 3))
    assert False
except:
    assert True