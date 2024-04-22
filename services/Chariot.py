from services.instances import StandardInstance
import threading

class Chariot(StandardInstance):
    def __init__(self, identifier, max_cpu):
        super().__init__(identifier, max_cpu)
        

    def process_request(self, request):
        if self.state == 0:
            return False
            
        if not self.can_handle_request(request):
                #self.request_queue.append(request)
            self.check_and_update_state()  # Check if the service should go down
        else:
            self.current_cpu += request.computation
            self.check_and_update_state()
    
    def check_and_update_state(self):
            # Method to check service's health and update state accordingly
        if self.current_cpu > self.max_cpu:
            self.state = 0  # Set state to unavailable if service is overloaded
        else:
            self.state = 1  # Otherwise, ensure it's marked as available

    def get_instance_identifier(self):
        return self.identifier

    