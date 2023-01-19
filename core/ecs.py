class Component():
    '''
    Base class which every component will inherent from.
    '''
    pass

class System():
    '''
    Base class which every system will inherent from.
    '''
    def __init__(self):
        self.registered_entities = []
        self.world = None

    def register_entity(self, entity):
        for current_entity in self.registered_entities:
            if current_entity.entity_id == entity.entity_id:
                return
        self.registered_entities.append(entity)

    def unregister_entity(self, entity_id):
        for entity in self.registered_entities:
            if (entity.entity_id == entity_id):
                self.registered_entities.remove(entity)
                break

    def get_mask(self):
        return self.component_mask

    def run(event):
        pass

# TODO: add paired component support and move support of entities
# TODO: extract Entity wrapper and create an Entity Handler class
class World():
    '''
    Represent a classic ecs system.
    More can be read here: https://en.wikipedia.org/wiki/Entity_component_system
    '''
    class Entity_wrapper:
        '''
        Wrapper around an entity id.
        Makes the relationship between entities and components more "logical" from a users perspective
        '''
        def __init__(self, entity_id, world):
            self.entity_id = entity_id
            self.world = world

        def add_component(self, component):
            return self.world.add_component(self.entity_id, component)

        def remove_component(self, component):
            self.world.remove_component(self.entity_id, component)
        
        def query_components(self, components_types):
            return self.world.query_components(self.entity_id, components_types) 
        
        def query_components_all(self):
            return self.world.query_components_all(self.entity_id)

        def disable_components(self, component_types):
            return self.world.disable_component(self.entity_id,component_types)

        def enable_components(self, component_types):
            return self.world.enable_component(self.entity_id,component_types)

        def disable_group(self, component_types, group_name):
            return self.world.disable_group(self.entity_id,component_types,group_name)

        def enable_group(self, group_name):
            return self.world.enable_group(self.entity_id,group_name)

        def destroy_entity(self):
            self.world.destroy_entity(self.entity_id)

    def __init__(self):
        self.systems = [] 
        self.entities = []  
        self.components = {} 
        self.disabled_components = {}
        self.next_entity_id = 0

    def _entity_conforms_with_mask(self, entity, mask):
        count = 0
        for mask_component_type in mask:
            if not mask_component_type in self.components:
                return 
            for current_entity,current_component in self.components[mask_component_type]:
                if current_entity == entity:
                    count += 1
                    break
        return count == len(mask)

    def _entity_exists(self, entity):
        if entity in self.entities:
            return True
        return False

    def create_entity(self):
        self.entities.append(self.next_entity_id)
        entity_wrapper = self.Entity_wrapper(self.next_entity_id, self)
        self.next_entity_id += 1
        return entity_wrapper

    def destroy_entity(self, entity):
        if not self._entity_exists(entity):
            raise Exception("Entity does not exist '" + str(entity) + "'") 
        for component_type in self.components:
            self.remove_component(entity, component_type)
        self.entities.remove(entity)

    def get_entities(self, mask):
        lst = []
        for entity in self.entities:
            if self._entity_conforms_with_mask(entity, mask):
                lst.append(self.Entity_wrapper(entity, self))
        return lst

    # OBS: if entity already has a component with the same type, then the old component will get replaced
    def add_component(self, entity, component):
        if not self._entity_exists(entity):
            raise Exception("Entity does not exist '" + str(entity) + "'") 
        component_type = type(component)
        if not component_type in self.components:
            self.components[component_type] = []
        for current_entity,current_component in self.components[component_type]:
            if current_entity == entity:
                self.components[component_type].remove((current_entity,current_component))
                break
        self.components[component_type].append((entity, component))

        for system in self.systems:
            if self._entity_conforms_with_mask(entity, system.get_mask()):
                system.register_entity(self.Entity_wrapper(entity, self))
            else:
                system.unregister_entity(entity) 
        return self.components[component_type][-1][1]

    def remove_component(self, entity, component_type):
        if not self._entity_exists(entity):
            raise Exception("Entity does not exist") 
        if not component_type in self.components:
            return
        
        # TODO: Make faster.
        # Instead of using remove we can swap the found entity-component pair with the last one in the list and decrement the list size
        # This procedure takes O(n) instead of O(n^2)
        for current_entity,current_component in self.components[component_type]:
            if (current_entity == entity):
                self.components[component_type].remove((current_entity, current_component))
                break
        for system in self.systems:
            if self._entity_conforms_with_mask(entity, system.get_mask()):
                system.register_entity(self.Entity_wrapper(entity, self))
            else:
                system.unregister_entity(entity) 

    def query_components(self, entity, components_types):
        if not self._entity_exists(entity):
            raise Exception(f"Entity '{entity}' does not exit")
        ans = []
        for component_type in components_types:
            if not component_type in self.components:
                # raise Exception(f"Component with type \'{component_type}\' not valid")
                # TODO: fix
                continue
            for current_entity,current_component in self.components[component_type]:
                if (current_entity == entity):
                    ans.append(current_component) 
                    break
        return ans
    
    def query_components_all(self, entity):
        lst = []
        if not self._entity_exists(entity):
            raise Exception(f"Entity '{entity}' does not exit")
        for component_type in self.components:
            for current_entity,current_component in self.components[component_type]:
                if (current_entity == entity):
                    lst.append(current_component)      
        return lst

    def _disable_component(self, entity, component_type, group_name):
        component = self.query_components(entity, [component_type])  
        if len(component) == 0:
            raise Exception(f"Component type '{component_type}' can not be disabled")
        self.remove_component(entity, component_type)  
        if not component_type in self.disabled_components:
            self.disabled_components[component_type] = []
        for current_entity,_,__ in self.disabled_components[component_type]:
            if current_entity == entity:
                raise Exception(f"Component type '{component_type}' is already disable")
        self.disabled_components[component_type].append((entity, component[0], group_name))

    def disable_group(self, entity, component_types: list, group_name):
        if not self._entity_exists(entity):
            raise Exception(f"Entity '{entity}' does not exit")
        for component in component_types:
            self._disable_component(entity, component, group_name)

    def disable_components(self, entity, component_types):
        self.disable_component_group(entity, component_types, None)

    def _enable_component(self, entity, component_type):
        # TODO: don't assume component_type exists in disabled_components
        for current_entity,current_component,_ in self.disabled_components[component_type]:
            if (current_entity == entity):
                self.add_component(entity, current_component)
                self.disabled_components[component_type].remove((current_entity, current_component, _))
                return
        # raise Exception(f"Component type '{component_type}' is already enabled")

    def enable_components(self, entity, components):
        if not self._entity_exists(entity):
            raise Exception(f"Entity '{entity}' does not exit")
        for component in components:
            self._enable_component(entity, component) 

    def enable_group(self, entity, group_name):
        if not self._entity_exists(entity):
            raise Exception(f"Entity '{entity}' does not exit")
        remove_lst = []
        for component_type in self.disabled_components:
            for current_entity,current_component,current_name in self.disabled_components[component_type]:
                if (current_entity == entity and current_name == group_name):
                    self.add_component(entity, current_component)
                    remove_lst.append((component_type, (current_entity, current_component, current_name)))
        for comp in remove_lst:
            self.disabled_components[comp[0]].remove(comp[1])

    def add_system(self, system):
        if system in self.systems:
            return
        system.world = self
        self.systems.append(system)
        # TODO: add entities to the system
        return system

    def remove_system(self, system_type):
        for system in self.systems:
            if type(system) == system_type:
                self.systems.remove(system)

    def run(self, dt):
        for system in self.systems:
            system.run(dt)
