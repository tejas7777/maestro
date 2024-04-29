from termcolor import colored
from services.resource.compute import Compute
from services.database_service import DatabaseService

class StandardInstance():
    def __init__(self, identifier, max_cpu, instance_compute_type="Standard"):
        self.compute = Compute()
        self.identifier = identifier
        
        if instance_compute_type == 'Standard-plus':
            self.max_cpu = self.compute.get_standard_plus_compute()
        else:
            self.max_cpu = self.compute.get_standard_compute()

        self.current_cpu = 0
        self.unprocessed_request_queue = []
        self.state = 1
        self.request_processed = 0
        self.up_scaled = 0
        self.restart_count = 0
        self.instance_compute_type = instance_compute_type
        self.restart_initiated = 0
        self.database_instance = None



    def set_state(self, new_state):
        print(f"State changing from {self.state} to {new_state} for {self.identifier}")
        self.state = new_state

    def process_request(self, request):
        if self.can_handle_request(request):
            self.current_cpu += request.computation
            self.request_processed += 1
        else:
            self.unprocessed_request_queue.append(request)
            self.set_state(0)

    def can_handle_request(self, request):
        if self.state == 0:
            return False
        return self.current_cpu + request.computation <= self.max_cpu
    
    
    def release_resources(self, computation):
        # Method to release resources after processing a request
        if self.state == 0:
            return  # Do not release resources if service is down
            
        self.current_cpu -= computation  # Subtract the computation cost
        self.current_cpu = max(0, self.current_cpu)  # Prevent negative CPU usage

    def set_service_down(self):
        self.set_state(0)
        #self.current_cpu = 0

    def get_instance_identifier(self):
        return self.identifier
    
    def scale_up(self):
        self.max_cpu = self.compute.get_standard_plus_compute()
        self.up_scaled = 0
        self.instance_compute_type = "Standard-Plus"

    def restart(self):
        self.set_state(1)
        self.current_cpu = 0
        # self.request_processed = 0
        self.restart_count += 1
        self.restart_initiated = 0

    def connect_to_database(self, database_instance: DatabaseService):
        if database_instance.connect():
            self.database_instance = database_instance
            print(colored(f"service {self.identifier} Connected to database {database_instance.get_instance_identifier()}", 'green'))
            return True
        else:
            print(f"service {self.identifier} Failed to connect to database {database_instance.get_instance_identifier()}")
            return False



