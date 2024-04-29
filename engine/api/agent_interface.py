from engine.meta.enviornment import Environment

class EnviornmentAgentInterface():
    def __init__(self, environment:Environment) -> None:
        self.enviornment = environment

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
        pass