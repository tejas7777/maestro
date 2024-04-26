class Environment:
    def __init__(self, services, load_balancer, meta_layer, time):
        self.services = services
        self.load_balancer = load_balancer
        self.meta_layer = meta_layer
        self.time = time
