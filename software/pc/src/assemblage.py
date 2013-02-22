class Assembler(object):
    
    def __init__(self, parent=None):
        """
        Assembler constructor.
        
        parent: an optional parent assembler.
        """
        self.services = {}
        self.cache = {}
        self.parent = parent
        #self.register("assembler",assembler, factory=(lambda *deps : self))
    
    def register(self, id, type, requires=None, factory=None, cacheable=True): #@ReservedAssignment
        """
        Register a new type for construction.
        
        type: the type to be registered.
        requires: an optional list of the types of the dependencies required by instances of the given type.
        factory: an optional factory method capable of building instances of the given type.
        cacheable: whether produced instances of the given type should be cached for reuse. 
        """
        dependencies = requires or []
        factory = factory or (lambda *deps : self.__build(type, deps))
        self.services[id] = type_information(type, factory, dependencies, cacheable)
        
    def __build(self, type, dependencies): #@ReservedAssignment
        return type(*dependencies)
    
    def spawn_child(self):
        """
        Produce an child assembler.
        
        Child assemblers have access to all registered types and cached instances present in
        any of its ancestors.
        """
        return assembler(parent=self)

    def provide(self, id): #@ReservedAssignment
        """
        Provide a instance of the desired type.
        
        If the type is cacheable, it will reuse a previously build instance instead of building a new one.
        
        type: the desired type.
        """
        if (not self._can_build_type(id)):
            raise ValueError("Can't build instance for unregistered type %s" % id)
        
        cached_instance = self._retrieve_from_cache(id)
        if (cached_instance is not None):
            return cached_instance
        
        new_instance = self._build_new(id)
        self._add_to_cache(id, new_instance)
        return new_instance
        
    def reset(self):
        for service in self.cache:
            del service
        self.cache = {}
        self.service = {}

    def _can_build_type(self, id): #@ReservedAssignment
        if (id in self.services):
            return True
        if (self.parent and self.parent._can_build_type(id)):
            return True
        return False
    
    def _retrieve_from_cache(self, id): #@ReservedAssignment
        if (id in self.cache.keys()):
            return self.cache[id]
        if (self.parent):
            return self.parent._retrieve_from_cache(id)
        return None
    
    def _build_new(self, id): #@ReservedAssignment
        dependencies = self._build_dependencies(id)
        return self._type_information(id).factory(*dependencies)

    def _build_dependencies(self, id): #@ReservedAssignment
        dependencies = []
        for each in self._type_information(id).dependencies:
            dependencies.append(self.provide(each))
        return dependencies
  
    def _add_to_cache(self, id, instance): #@ReservedAssignment
        if (self._type_information(id).cacheable):
            self.cache[id] = instance

    def _type_information(self, id): #@ReservedAssignment
        if (id in self.services):
            return self.services[id]
        if (self.parent):
            return self.parent._type_information(id)
        return None
    

class type_information(object):
    
    def __init__(self, type, factory, dependencies, cacheable):
        self.type = type
        self.factory = factory
        self.dependencies = dependencies
        self.cacheable = cacheable
