class Environment:
    def __init__(self, service, load_balancer, meta_layer, time):
        self.services = service
        self.load_balancer = load_balancer
        self.meta_layer = meta_layer
        self.time = time
