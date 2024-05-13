class DatabaseService:

    def __init__(self, identifier, max_connections = 10):
        self.max_connections = max_connections
        self.max_disk_io = 500
        self.current_connections = 0
        self.current_disk_io = 0
        self.state = 1
        self.identifier = identifier
        self.restart_initiated = 0
        self.restart_count = 0


    def connect(self):
        if  self.current_connections >= self.max_connections:
            return False
        
        self.current_connections += 1

        return True
    
    def health_check(self):
        return self.state
    
    def set_state(self, state):
        self.state = state

    def get_instance_identifier(self):
        return self.identifier
    
    def can_handle_disk_io(self, disk_io):
        if self.state == 0:
            return False
        
        return self.current_disk_io + disk_io < self.max_disk_io
    
    def handle_disk_io(self, io):
        if self.can_handle_disk_io(io):
            self.current_disk_io += io
            return True
        return False
    
    def set_service_down(self):
        self.set_state(0)
        self.current_connections = 0
        self.current_disk_io = 0

    def release_resources(self, disk_io):
        if self.state == 0:
            return
           
        self.current_disk_io -= disk_io
        self.current_cpu = max(0, self.current_disk_io)

    def terminate_connection(self):
        self.current_connections -= 1