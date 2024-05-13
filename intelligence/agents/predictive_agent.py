from termcolor import colored
from engine.api.agent_interface import EnviornmentAgentInterface
from intelligence.utils.enkf_compute import EnsembleKalmanFilterCompute as EnKFCompute
from engine.utils.statistics_collector import AgentStatisticsCollector

class RecoveryAgentPredictive:
    def __init__(self, agent_id: str, agent_type: str, enviornment_interface: EnviornmentAgentInterface, agent_statistics_collector: AgentStatisticsCollector = None):
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
        self.agent_statistics_collector = agent_statistics_collector


    def send_recover_service_request(self,service_identifier: str):
        self.enviornment_interface.restart_service(service_identifier, 2)
        
    def monitor_service_loads(self, prediction = None):
        #Placeholder scale out logic
        avg_cpu_usage = 0

        if prediction:
            avg_cpu_usage = prediction
        else:
            avg_cpu_usage= self.enviornment_interface.get_avg_system_load()

        print(colored(f"[monitor_service_loads] {avg_cpu_usage}", "yellow"))

        max_db_connections_available = self.enviornment_interface.get_max_db_connections()


        if avg_cpu_usage > 130 and avg_cpu_usage < 250:
            if self.scale_out_count < self.max_scale_out_instances and max_db_connections_available > 0:
                print(colored(f"[recovery_agent][monitor_service_loads][SCALE_OUT]", "green"))
                self.scale_out_instances()
                self.scale_out_count += 1

        elif avg_cpu_usage > 250 and self.scale_up_count < self.max_scale_up:
                #Least used instance should scale up
                print(colored(f"[recovery_agent][monitor_service_loads][SCALE_UP]", "green"))
                self.scale_up_instances()
                self.scale_up_count += 1
            

        elif avg_cpu_usage < 70 and self.scale_out_count > 0:
            #print(colored(f"Scaling out Down!!", "red"))
            self.epochs += 1
            if self.epochs > 5:
                self.epochs = 0
                self.enviornment_interface.stop_scaled_out_instances(1)
            #self.enviornment_interface.stop_scaled_out_instances()



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

        if self.agent_statistics_collector:
            self.agent_statistics_collector.collect_kalman_prediction_data(minuite=self.enviornment_interface.get_current_time(), prediction=prediction)
        
        self.monitor_service_loads(prediction=prediction)

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


        
        

            
            


        

        
