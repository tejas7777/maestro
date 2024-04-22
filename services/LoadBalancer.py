class LoadBalancer:
    def __init__(self):
        self.services = []
        self.index = 0  # for round-robin strategy

    def register_service(self, *args):
        for arg in args:
            self.services.append(arg)

    def get_service_round_robin(self):
        # Simple round-robin load balancing, returns one service at a time
        if not self.services:
            return None
        service = self.services[self.index]
        self.index = (self.index + 1) % len(self.services)
        return service

    def get_service_least_cpu(self):
        # Get the service with the least current CPU usage that is still operational
        available_services = [s for s in self.services if s.state != 0]
        if not available_services:
            return None
        # Return one service with the minimum CPU usage
        return min(available_services, key=lambda x: x.current_cpu)

    def deregister_service(self, service):
        # Remove a service from the list, if necessary
        if service in self.services:
            self.services.remove(service)