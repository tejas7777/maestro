from termcolor import colored
from engine.api.agent_interface import EnviornmentAgentInterface
from intelligence.utils.enkf import EnsembleKalmanFilter

class RecoveryAgent:
    def __init__(self, agent_id: str, agent_type: str, enviornment_interface: EnviornmentAgentInterface):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.enviornment_interface = enviornment_interface
        self.max_scale_out_instances = 5 #placeholder
        self.scale_out_count = 0
        self.request_rate = 100
        self.enkf = EnsembleKalmanFilter(ensemble_size=100, initial_state=self.request_rate, process_noise_cov=0.1)


    def send_recover_service_request(self,service_identifier: str):
        self.enviornment_interface.restart_service(service_identifier, 2)
        
    def monitor_service_loads(self):
        #Placeholder scale out logic
        avg_cpu_usage= self.enviornment_interface.get_avg_system_load()

        print(colored(f"Average system load: {avg_cpu_usage}", "yellow"))

        max_db_connections = self.enviornment_interface.get_max_db_connections()


        if avg_cpu_usage > 120 and self.scale_out_count < self.max_scale_out_instances and max_db_connections > 0:
            print(colored(f"Scaling out!!", "green"))
            self.scale_out_instances()
            self.scale_out_count += 1

        elif avg_cpu_usage < 70 and self.scale_out_count > 0:
            #print(colored(f"Scaling out Down!!", "red"))
            self.enviornment_interface.stop_scaled_out_instances()


        

    def watch(self):
        meta_data:dict = self.enviornment_interface.get_meta_data()

        if len(self.enviornment_interface.comm_for_agents) > 0:
            for comm in self.enviornment_interface.comm_for_agents:
                if comm["agent_id"] == self.agent_id:
                    if comm["type"] == "service_terminated":
                        service_identifier = comm["service_identifier"]
                        print(colored(f"Service {service_identifier} terminated", "red"))
                        self.scaled_out_termination_callback()
                        self.enviornment_interface.comm_for_agents.pop()

        instances:dict[str:dict] = meta_data["instances"]
        #check instance state
        for instance_identifier, instance_data in instances.items():
            if instance_data["status"] == 0 and instance_data.get("restart_initiated") == 0:
                print(colored(f"Service {instance_identifier} recovery request sent by agent", "yellow"))
                self.send_recover_service_request(instance_identifier)

        #TEST Make a prediction

        self.enkf.predict()
        prediction = self.enkf.get_mean_prediction()

        print(colored(f"[recovery_agent][watch][kalman prediction] {prediction}" , "yellow") )
        
        self.monitor_service_loads()

    def scale_out_instances(self,num = 1):
        self.enviornment_interface.add_new_instances(num)

    def scaled_out_termination_callback(self):
        self.scale_out_count -= 1

    def update_observations(self,data: dict):
        if data["request_rate"]:
            self.enkf.update(data["request_rate"])

            
            


        

        
