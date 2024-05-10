from engine.meta.enviornment import Environment

class EnviornmentAgentInterface():
    def __init__(self, environment:Environment) -> None:
        self.enviornment = environment
        self.comm_for_agents = self.enviornment.comms_for_agents

    def restart_service(self, service_identifier: str, restart_time_in_minuites: int) -> None:

        service = self.enviornment.get_service_by_identifier(service_identifier)
        service.restart_initiated = 1
        
        self.enviornment.environment_task_queue.append({
            "service": service,
            "time": self.enviornment.time.get_increment_minutes_str(restart_time_in_minuites, self.enviornment.time.hour, self.enviornment.time.day),
            "type": "restart_service"
        })

    def get_meta_data(self):
        return self.enviornment.meta_layer.get_data()
    
    def add_new_instances(self,num, type='Standard'):
        self.enviornment.environment_task_queue.append({
            "num": num,
            "type": "add_new_instances",
            "instance_type": type,
            "time": self.enviornment.time.get_increment_minutes_str(2, self.enviornment.time.hour, self.enviornment.time.day)
        })

    def scale_up_instances(self,num, type='Standard'):
        self.enviornment.environment_task_queue.append({
            "num": num,
            "type": "scale_up_instances",
            "instance_type": type,
            "time": self.enviornment.time.get_increment_minutes_str(1, self.enviornment.time.hour, self.enviornment.time.day)
        })

    def add_new_db_instances(self, num = 1, unconnected_services = []):
        self.enviornment.environment_task_queue.append({
            "num": num,
            "type": "add_new_db_instances",
            "unconnected_services": unconnected_services,
            "instance_type": "DB",
            "time": self.enviornment.time.get_increment_minutes_str(3, self.enviornment.time.hour, self.enviornment.time.day)
        })
    
    def get_avg_system_load(self):
        total_cpu = 0
        for service in self.enviornment.services:
            total_cpu += service.current_cpu

        num = len(self.enviornment.services)

        return total_cpu / num
    
    def stop_scaled_out_instances(self, num = 0):
        #Get scaled out instances
        scaled_out_instances = [ service for service in self.enviornment.services if service.scaled_out == 1]

        if len(scaled_out_instances) == 0:
            return

        if num == 0:
            num = len(scaled_out_instances)

        #Send for termination
        smooth_out_time = 1
        for instance in scaled_out_instances[:num]:
            self.enviornment.environment_task_queue.append({
                "service": instance,
                "time": self.enviornment.time.get_increment_minutes_str(smooth_out_time, self.enviornment.time.hour, self.enviornment.time.day),
                "type": "terminate_service"
            })
            smooth_out_time += 1

    def service_termination_callback(self, service_identifier: str):
        self.comm_for_agents.append({
            "agent_id": "recovery-agent",
            "type": "service_terminated",
            service_identifier: service_identifier
        })

    def get_max_db_connections(self):
        return self.enviornment.get_available_db_connections()
    
    def register_service_with_load_balancer(self, services: list = []):

        for service in services:
            self.enviornment.load_balancer.register_service(service)

    def deregister_service_with_load_balancer(self, services: list = []):

        for service in services:
            self.enviornment.load_balancer.deregister_service(service)

    def get_active_service_list(self):
        all_services = self.enviornment.services

        if all_services == None:
            #TODO: Do better
            return ['No services found']
        return [ services for services in all_services if services.state == 1 ]
    
    def get_envrioment_config(self) -> dict[str, dict]:
        if self.enviornment.config == None:
            return {
                "system":{},
                "agent":{}
            }
        
        return self.enviornment.config