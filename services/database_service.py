class DataBaseService:

    def __init__(self, identifier):
        self.max_connections = 10
        self.max_disk_io = 500
        self.current_connections = 0
        self.current_disk_io = 0
        self.status = 1
        self.identifier = identifier


    def connect(self):
        if  self.current_connections >= self.max_connections:
            return False
        
        self.current_connections += 1

        return True
    
    def health_check(self):
        return self.status
    
    def set_status(self, status):
        self.status = status