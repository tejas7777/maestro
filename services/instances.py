class StandardInstance():
    def __init__(self, identifier, max_cpu):
        self.identifier = identifier
        self.max_cpu = max_cpu
        self.current_cpu = 0
        self.request_queue = []
        self.state = 1

    def set_state(self, new_state):
        print(f"State changing from {self.state} to {new_state} for {self.identifier}")
        self.state = new_state

    def process_request(self, request):
        if self.can_handle_request(request):
            self.current_cpu += request.computation
            # if not self.check_health():
            #     self.set_state(0)
        else:
            self.request_queue.append(request)
            self.set_state(0)

    def can_handle_request(self, request):
        if self.state == 0:
            return False
        return self.current_cpu + request.computation <= self.max_cpu
    
    # def check_health(self):
    #     overloaded = self.current_cpu > self.max_cpu
    #     if overloaded:
    #         self.set_state(0)

    #     return not overloaded
    
    def release_resources(self, computation):
        # Method to release resources after processing a request
        if self.state == 0:
            return  # Do not release resources if service is down
            
        self.current_cpu -= computation  # Subtract the computation cost
        self.current_cpu = max(0, self.current_cpu)  # Prevent negative CPU usage

    def set_service_down(self):
        self.set_state(0)


