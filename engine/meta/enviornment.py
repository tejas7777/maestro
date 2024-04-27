from services.instances import StandardInstance
from services.LoadBalancer import LoadBalancer
from engine.meta.layer import MetaLayer
from engine.utils.time_data import TimeData
from termcolor import colored

class Environment:
    def __init__(self, services: list[StandardInstance], load_balancer: LoadBalancer, meta_layer: MetaLayer, time: TimeData,
                 environment_task_queue: list = []):
        self.services = services
        self.load_balancer = load_balancer
        self.meta_layer = meta_layer
        self.time = time
        self.environment_task_queue = environment_task_queue

    def __execute_task_at_current_time(self):

        current_time = self.time.get_current_time_str()
        for i in range(len(self.environment_task_queue)):
            try:
                task = self.environment_task_queue[i]
                if task['time'] == current_time:
                    if task['type'] == 'restart_service':
                        service: StandardInstance = self.get_service_by_identifier(task['service'].identifier)
                        service.restart()
                        print(colored(f"Service {service.identifier} restarted",'yellow'))
                        self.load_balancer.register_service(service)
                        task["status"] = "completed"
            except Exception as e:
                print(colored(f"[Enviornment][execute_task_at_current_time] Error executing task: {e}", 'red'))
                
        self.environment_task_queue = [task for task in self.environment_task_queue if task.get("status") != "completed"]

            

        

    def get_service_by_identifier(self, identifier: str):
        for service in self.services:
            if service.identifier == identifier:
                return service
        return None
    
    
    def update_environment(self):
        self.__execute_task_at_current_time()