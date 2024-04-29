from services.instances import StandardInstance
from services.LoadBalancer import LoadBalancer
from engine.meta.layer import MetaLayer
from engine.utils.time_data import TimeData
from termcolor import colored
from services.database_service import DatabaseService

class Environment:
    def __init__(self, services: list[StandardInstance], load_balancer: LoadBalancer, meta_layer: MetaLayer, time: TimeData,
                 environment_task_queue: list = [], database_services: list = [DatabaseService]):
        self.services = services
        self.load_balancer = load_balancer
        self.meta_layer = meta_layer
        self.time = time
        self.environment_task_queue = environment_task_queue
        self.database_services = database_services

    def __execute_task_at_current_time(self):

        current_time = self.time.get_current_time_str()

        #print(colored(f"Executing tasks at time {current_time} {self.environment_task_queue}", 'yellow'))
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
                        self.__skip_resource_release(service.identifier)

                    if task['type'] == 'release_resources':
                        service: StandardInstance = task['service']
                        if service.state == 0:
                            task["status"] = "skipped"
                            continue
                        service.release_resources(task["computation"])
                        print(colored(f"Service {service.identifier} resources released", 'yellow'))
                        self.load_balancer.register_service(service)
                        task["status"] = "completed"

                    if task['type'] == 'release_database_resources':
                        database: DatabaseService = task['database']
                        if database.state == 0:
                            task["status"] = "skipped"
                            continue
                        database.release_resources(task["disk_io"])
                        print(colored(f"database {database.identifier} resources released", 'yellow'))
                        task["status"] = "completed"
                    
                    
            except Exception as e:
                print(colored(f"[Enviornment][execute_task_at_current_time] Error executing task: {e}", 'red'))

        self.environment_task_queue = [task for task in self.environment_task_queue if task.get("status") not in ["completed", "skipped"]]


    def __skip_resource_release(self, service_identifier: str):

        for i in range(len(self.environment_task_queue)):
            task = self.environment_task_queue[i]
            if task['type'] == 'release_resources' and task['service'].identifier == service_identifier:
                task["status"] = "skipped"
                #print(colored(f"Skipping resource release for service {service_identifier} as it is not in running state", 'yellow'))
                break

        
        

    def get_service_by_identifier(self, identifier: str):
        for service in self.services:
            if service.identifier == identifier:
                return service
        return None
    
    
    def update_environment(self):
        self.__execute_task_at_current_time()

    def add_new_instances(self, num_instances, type = "Standard"):
        
        current_num = len(self.services)

        for i in range(num_instances):
            instance = StandardInstance(f'instance-{ current_num + i }', instance_compute_type=type)
            self.services.append(instance)
            instance_data = {
                "cpu_usage":instance.current_cpu,
                "requests_processed":instance.request_processed,
                "status":instance.state,
                "scaling_events":0,
                "max_cpu":instance.max_cpu,
                "instance_type":instance.instance_compute_type,
                "restart_initiated":instance.restart_initiated,
                "restart_count":instance.restart_count
            }
            self.meta_layer.upsert_instance_data(instance.get_instance_identifier(), instance_data)
            self.load_balancer.register_service(instance)

        
