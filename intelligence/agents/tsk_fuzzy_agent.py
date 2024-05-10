from termcolor import colored
from engine.api.agent_interface import EnviornmentAgentInterface
from intelligence.utils.enkf_compute import EnsembleKalmanFilterCompute as EnKFCompute
from intelligence.utils.tsk_fuzzy import TSKFuzzySystem
import numpy as np

class RecoveryAgentTSK:
    def __init__(self, agent_id: str, agent_type: str, enviornment_interface: EnviornmentAgentInterface):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.enviornment_interface = enviornment_interface
        self.config = enviornment_interface.get_envrioment_config()
        self.max_scale_out_instances =  self.config["agent"].get("max_scale_out_instances",2)
        self.scale_out_count = 0
        self.enkf = EnKFCompute(ensemble_size=100, initial_state=100, process_noise_cov=0.1)
        self.max_db_scale_out = self.config["agent"].get("max_db_scale_out",2)
        self.db_scale_out_count = 0
        self.max_scale_up =  self.config["agent"].get("max_scale_up_instances",4)
        self.scale_up_count = 0
        self.epochs = 0
        self.fuzzy_system = TSKFuzzySystem()
        self.meta_data:dict = None
        self.initialize_fuzzy_rules()
        self.first_run_completed = False

    def initialize_fuzzy_rules(self):
        # Define fuzzy rules based on CPU and request load
        self.fuzzy_system.add_rule(
            lambda inputs: min(self.cpu_load_high(inputs['cpu_load']), self.request_load_low(inputs['request_load'])),
            (0.005, 0.005, -1) 
        )
        self.fuzzy_system.add_rule(
            lambda inputs: min(self.cpu_load_low(inputs['cpu_load']), self.request_load_high(inputs['request_load'])),
            (-0.005, -0.005, 1)
        )
        self.fuzzy_system.add_rule(
            lambda inputs: self.service_down_high(inputs['down_percentage']),
            (0, 0, 0, 1) 
        )

    def cpu_load_high(self, cpu_load):
        return np.clip((cpu_load - 30) / 40, 0, 1)
    
    def cpu_load_low(self, cpu_load):
        return np.clip((40 - cpu_load) / 20, 0, 1)

    def request_load_high(self, request_load):
        return np.clip((request_load - 50) / 150, 0, 1)
    
    def request_load_low(self, request_load):
        return np.clip((request_load - 30) / 70, 0, 1)

    def service_down_low(self, down_percentage):
        return np.clip(30 - down_percentage / 20, 0, 1)
    
    def service_down_high(self, down_percentage):
        return np.clip((down_percentage - 20) / 20, 1, 0)

    def send_recover_service_request(self,service_identifier: str):
        self.enviornment_interface.restart_service(service_identifier, 2)
        
    def monitor_service_loads(self, prediction = None):
        avg_cpu_usage = prediction if prediction is not None else self.enviornment_interface.get_avg_system_load()
        request_load = self.meta_data["system_data"]["total_requests_processed"] + self.meta_data["system_data"]["total_requests_unprocessed"]
        down_count = len([instance for instance in self.meta_data["instances"].values() if instance["status"] == 0 and instance.get("restart_initiated") != 1])
        total_instances = len(self.meta_data["instances"])
        down_percentage = (down_count / total_instances) * 100 #Dangerous if total_instances is 0!!!

        max_db_connections_available = self.enviornment_interface.get_max_db_connections()

        print(colored(f"[monitor_service_loads] {avg_cpu_usage}", "yellow"))

        inputs = {
            'cpu_load': avg_cpu_usage,
            'request_load': request_load,
            'down_percentage': down_percentage
        }
        scaling_action = self.fuzzy_system.evaluate(inputs)

        print(colored(f"[monitor_service_loads][scaling_action] {scaling_action}", "yellow"))

        if scaling_action > 0.5:
            if self.scale_out_count < self.max_scale_out_instances and max_db_connections_available > 0:
                print(colored(f"[recovery_agent][monitor_service_loads][SCALE_OUT]", "green"))
                self.scale_out_instances()
                self.scale_out_count += 1
            elif self.scale_up_count < self.max_scale_up:
                print(colored(f"[recovery_agent][monitor_service_loads][SCALE_UP]", "green"))
                self.scale_up_instances()
                self.scale_up_count += 1

        elif scaling_action < -0.5 and self.scale_out_count > 0:
            self.epochs += 1
            if self.epochs > 5:
                self.epochs = 0
                print(colored(f"[recovery_agent][monitor_service_loads][SCALE_DOWN]", "red"))
                self.enviornment_interface.stop_scaled_out_instances(1)



    def handle_unconnected_services(self, unnconnected_services: list):
        avg_cpu_usage= self.enviornment_interface.get_avg_system_load()

        #derigister services from load balancer
        if len(unnconnected_services) > 0:
            self.enviornment_interface.deregister_service_with_load_balancer(unnconnected_services)

        if self.db_scale_out_count < self.max_db_scale_out:
            if (avg_cpu_usage > 200 and len(unnconnected_services) > 0) or len(unnconnected_services) / len(self.enviornment_interface.get_active_service_list()) > 0.2:
                print(colored(f"[recovery_agent][handle_unconnected_services] Scaling out DB", "green"))
                self.enviornment_interface.add_new_db_instances(1, unconnected_services=unnconnected_services)
                self.db_scale_out_count += 1


    def watch(self):
        meta_data:dict = self.enviornment_interface.get_meta_data()
        self.meta_data:dict = meta_data #Very hacky way of coding, need to do better

        if len(self.enviornment_interface.comm_for_agents) > 0:
            for comm in self.enviornment_interface.comm_for_agents:
                if comm["agent_id"] == self.agent_id:
                    if comm["type"] == "service_terminated":
                        service_identifier = comm["service_identifier"]
                        print(colored(f"Service {service_identifier} terminated", "red"))
                        self.scaled_out_termination_callback()
                        self.enviornment_interface.comm_for_agents.pop()
                    if comm["type"] == "db_unconnected_services":
                        print(colored(f"DB unconnected services: {comm['services']}", "red"))
                        #Add Processing Logic
                        self.handle_unconnected_services(comm["services"])
                        self.enviornment_interface.comm_for_agents.pop()

                    if comm["type"] == "db_connected_services_success":
                        print(colored(f"DB connected services: {comm['services']}", "green"))
                        self.enviornment_interface.register_service_with_load_balancer(comm["services"])
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
        
        if self.first_run_completed:
            #self.update_observations(data=meta_data["system_data"])
            self.monitor_service_loads(prediction=prediction)

        self.first_run_completed = True

    def scale_out_instances(self,num = 1):
        self.enviornment_interface.add_new_instances(num)

    def scale_up_instances(self,num = 1):
        self.enviornment_interface.scale_up_instances(num)

    def scaled_out_termination_callback(self):
        self.scale_out_count -= 1

    def update_observations(self,data: dict):
        # if data["request_rate"]:
        #     self.enkf.update(data["request_rate"])

        if data["avg_cpu_usage"]:
            self.enkf.update(data["avg_cpu_usage"])

        
        

            
            


        

        
