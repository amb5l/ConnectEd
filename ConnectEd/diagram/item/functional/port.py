class Port:
    '''
    A port is a connection point between a diagram and the hierarchical
    level above, or the outside world.
    '''
    def __init__(self, name, direction, type, properties):
        '''
        Constructs a new instance of the port.
        '''
        self.name       = name
        self.direction  = direction
        self.type       = type
        self.properties = properties