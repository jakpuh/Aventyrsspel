# TODO: fix this import mess in every file
import sys

sys.path.insert(1, 'core')
import core
import components as comp
import events as evt
from object_storage import Object_storage
import random as rand
import math



def collision_event_pred_generator(entity1_comps: list, entity2_comps: list):
    '''
    Generates and returns a predicate function for callables who subscribe to collision events
    This predicate will check if the entity1 / entity2 have the components in the entity1_comps / entity2_comps lists
    This predicate will also put the entities in the order which their comps are in (e.g if entity2 has the components of entity1_comps then it will swap with entity1)
    '''
    # Lambda would be ideal for this case but it looks like pythons lambda doesn't support multiline...
    # This means we have to create a inner function and then return it instead; the reason this is possible is because python functions are actually objects which can store state
    # This wouldn't be possible if python functions behaved more like traditional functions which may lead to confusion
    def _(event: evt.Collision_event):
        # The order of the entities are not defined which means the entity correlated with entity1_comps or entity2_comps can be either entity1 or entity2
        entity1_1 = event.entity1.query_components(entity1_comps)
        entity1_2 = event.entity1.query_components(entity2_comps)
        entity2_1 = event.entity2.query_components(entity1_comps)
        entity2_2 = event.entity2.query_components(entity2_comps)
        if len(entity1_1) == len(entity1_comps) and len(entity2_2) == len(entity2_comps):
            return True
        if len(entity1_2) == len(entity2_comps) and len(entity2_1) == len(entity1_comps):
            tmp = event.entity1 
            event.entity1 = event.entity2
            event.entity2 = tmp
            return True
        return False
    return _
