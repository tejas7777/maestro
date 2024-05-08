from services.instances import StandardInstance
from services.LoadBalancer import LoadBalancer
from engine.meta.layer import MetaLayer
from engine.utils.time_data import TimeData
from termcolor import colored
from services.database_service import DatabaseService

class Environment:
    def __init__(self, services: list[StandardInstance], load_balancer: LoadBalancer, meta_layer: MetaLayer, time: TimeData,
                 environment_task_queue: list = [], database_services: list[DatabaseService] = []):
        self.services = services
        self.load_balancer = load_balancer
        self.meta_layer = meta_layer
        self.time = time
        self.environment_task_queue = environment_task_queue
        self.database_services = database_services
        self.comms_for_agents = []
        self.unprocessed_requests = 0

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
                        #print(colored(f"Service {service.identifier} resources released", 'yellow'))
                        self.load_balancer.register_service(service)
                        task["status"] = "completed"

                    if task['type'] == 'release_database_resources':
                        database: DatabaseService = task['database']
                        if database.state == 0:
                            task["status"] = "skipped"
                            continue
                        database.release_resources(task["disk_io"])
                        #print(colored(f"database {database.identifier} resources released", 'yellow'))
                        task["status"] = "completed"

                    if task['type'] == 'add_new_instances':
                        self.add_new_instances(task["num"], task["instance_type"])
                        task["status"] = 'completed'

                    if task['type'] == 'terminate_service':
                        service: StandardInstance = task['service']
                        service.terminate_service()
                        print(colored(f"Service {service.identifier} terminated", 'yellow'))
                        self.load_balancer.deregister_service(service)
                        if service in self.services:
                            self.services.remove(service)

                        self.comms_for_agents.append({
                            "agent_id": "recovery-agent",
                            "type": "service_terminated",
                            "service_identifier": service.identifier
                        })

                        task["status"] = 'completed'
                     
                    
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

    def assign_services_to_databases(self, instance_list: list[StandardInstance] = None):

        if not instance_list:
            instance_list = self.services

        db_index = 0
        for service in instance_list:
            attempts = 0
            while not service.database_instance and attempts < len(self.database_services):
                if not service.connect_to_database(self.database_services[db_index]):
                    attempts += 1
                db_index = (db_index + 1) % len(self.database_services)

    def add_new_instances(self, num_instances, type = "Standard"):
        
        current_num = len(self.services)
        new_instances = []

        for i in range(num_instances):
            instance = StandardInstance(f'standard-instance-{ current_num + i }', instance_compute_type=type, scaled_out= 1)
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
            new_instances.append(instance)
        
        self.assign_services_to_databases(new_instances)

        print(colored(f"Added {new_instances} ", 'green'))

    
    def add_intance_meta_data_v2(self,):

        instance_data_to_update = {
        }

        for instance in self.services:
            instance_data = {
                "cpu_usage":instance.current_cpu,
                "requests_processed":instance.request_processed,
                "status":instance.state,
                "up_scaled":instance.up_scaled,
                "max_cpu":instance.max_cpu,
                "instance_type":instance.instance_compute_type,
                "restart_initiated":instance.restart_initiated,
                "restart_count":instance.restart_count,
                "scaled_out":instance.scaled_out,
                "database_instance":instance.database_instance.get_instance_identifier() if instance.database_instance else None,
                "instance_compute_type": instance.instance_compute_type,
                "processed_request_count": instance.request_processed
            }

            instance_data_to_update[instance.get_instance_identifier()] = instance_data

        self.meta_layer.update_instance_data(instance_data_to_update)

    def update_time_in_meta_layer_v2(self):
        self.meta_layer.update_record_by_indentifier(
            identifier="time",
            data = self.time.get_current_time()
        )

    def get_avg_system_load_v2(self):
        total_cpu = 0
        for service in self.services:
            total_cpu += service.current_cpu

        num = len(self.services)

        return total_cpu / num

    def update_system_data(self):
        system_data_to_update = {
            "avg_cpu": self.get_avg_system_load_v2(),
            "total_requests_processed": sum([service.request_processed for service in self.services]),
            "total_requests_unprocessed": self.unprocessed_requests,
            "request_drop_rate": round( self.unprocessed_requests / (self.unprocessed_requests + sum([service.request_processed for service in self.services] 
                                                                                              if self.unprocessed_requests + sum([service.request_processed 
                                                                                                                                  for service in self.services]) 
                                                                                                                                  > 0 else 1) ), 2) * 100,
        }

        self.meta_layer.update_system_data(system_data_to_update)

    def update_meta_data_after_every_minuite_v2(self, data):
        self.unprocessed_requests += data["unprocessed_requests_for_min"]
        self.update_time_in_meta_layer_v2()
        self.add_intance_meta_data_v2()
        self.meta_layer.update_meta_data_cache()
        self.update_system_data()
        
    def get_available_db_connections(self):
        #Get total available db connections (max connections - current connections)
        return sum([db.max_connections - db.current_connections for db in self.database_services])

            
        


        
