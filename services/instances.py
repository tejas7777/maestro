class StandardInstance():
    def __init__(self, identifier, max_cpu):
        self.identifier = identifier
        self.max_cpu = max_cpu
        self.current_cpu = 0
        self.request_queue = []
        self.state = 1

    def process_request(self, request):
        if self.can_handle_request(request):
            self.current_cpu += request.computation
            if not self.check_health():
                self.state = 0
        else:
            self.request_queue.append(request)
            self.state = 0

    def can_handle_request(self, request):
        if self.state == 0:
            return False
        return self.current_cpu + request.computation <= self.max_cpu
    
    def check_health(self):
        overloaded = self.current_cpu > self.max_cpu
        if overloaded:
            self.state = 0
        else:
            self.state = 1
        return not overloaded


