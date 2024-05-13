from termcolor import colored
from engine.api.agent_interface import EnviornmentAgentInterface
from intelligence.utils.tsk_fuzzy import TSKFuzzySystem
import numpy as np
import math

'''

NOTE THIS AGENT IS DEPRECATED AND NOT USED IN THE FINAL IMPLEMENTATION

REFER to the final implementation in intelligence/agents/tsk_fuzzy_agent.py

'''

class FuzzyAgent:
    def __init__(self, agent_id: str, agent_type: str, enviornment_interface: EnviornmentAgentInterface):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.enviornment_interface = enviornment_interface
        self.max_scale_out_instances = 5 #placeholder
        self.scale_out_count = 0
        self.tsk_fuzzy_system = TSKFuzzySystem()
        self.meta_data = None
        self.init_fuzzy_system()

    def cpu_load_high(self, cpu_load):
        return np.clip((cpu_load - 30) / 40, 0, 1)
    
    def cpu_load_low(self, cpu_load):
        return np.clip((40 - cpu_load) / 20, 0, 1)

    def request_load_high(self, request_load):
        return np.clip((request_load - 50) / 150, 0, 1)
    
    def request_load_low(self, request_load):
        return np.clip((request_load- 30) / 70, 0, 1)

    def service_down_low(self, down_percentage):
        return np.clip(30-down_percentage/20, 0, 1)
    
    def service_down_high(self, down_percentage):
        return np.clip((down_percentage - 20) / 20, 0, 1)


    def init_fuzzy_system(self):
        #RULE CPU LOAD HIGH AND REQUEST LOAD HIGH AND SERVICE DOWN LOW
        self.tsk_fuzzy_system.add_rule(
            lambda data: min(self.cpu_load_high(data['cpu_load']), self.request_load_high(data['request_load']), self.service_down_low(data['down_percentage'])),
            (0.07, 0.03, -0.5,-1,-1)
        )

        #RULE SERVICE DOWN HIGH
        self.tsk_fuzzy_system.add_rule(
            lambda data: self.service_down_high(data['down_percentage']),
            (0, 0, 0, 0.5,-1)
        )

        #RULE CPU LOAD HIGH AND REQUEST LOAD HIGH AND SERVICE DOWN HIGH
        self.tsk_fuzzy_system.add_rule( 
            lambda data: min(self.cpu_load_high(data['cpu_load']), self.request_load_high(data['request_load']), self.service_down_high(data['down_percentage'])),
            (0.07, 0.03, 0.3,-1)
        )


    def send_recover_service_request(self,service_identifier: str):
        self.enviornment_interface.restart_service(service_identifier, 2)

    def get_system_data(self):
        try:
            down_count = len([instance for instance in self.meta_data["instances"].values() if instance["status"] == 0 and instance.get("restart_initiated") != 1])
            total_instances = len(self.meta_data["instances"])
            if total_instances == 0:
                print(colored("[intelligence][FuzzyAgent][get_system_data] No instances found",'red'))
                return None
            
            down_percentage = (down_count / total_instances) * 100

            total_cpu_usage = sum([instance["cpu_usage"] for instance in self.meta_data["instances"].values() if instance["status"] == 1])
            total_cpu_usage_available = sum([instance["max_cpu"] for instance in self.meta_data["instances"].values() if instance["status"] == 1 ])
            if total_cpu_usage_available == 0:
                print(colored("[intelligence][FuzzyAgent][get_system_data] No cpu usage available","red"))
                return None

            cpu_load = (total_cpu_usage / total_cpu_usage_available) * 100

            request_load = self.meta_data["system_data"]["total_requests_processed"] + self.meta_data["system_data"]["total_requests_unprocessed"]

            return {    
                "down_percentage": down_percentage,
                "cpu_load": cpu_load,
                "request_load": request_load,
            }
        except KeyError as e:
            print(colored(f"[intelligence][FuzzyAgent][get_system_data] Key Error: {e}", "red"))
            return None
    
    def scaling_out_decision(self):
        system_data = self.get_system_data() #Gets the current data of the system at this minute
        if system_data is None:
            print(colored("[intelligence][FuzzyAgent][scaling_out_decision] System data is None", "red"))
            return None
        
        scaling_score = self.tsk_fuzzy_system.evaluate({
            'cpu_load': system_data['cpu_load'],
            'request_load': system_data['request_load'],
            'down_percentage': system_data['down_percentage']
        })

        print(colored(f"Scaling Decision Score: {scaling_score:.2f}", "blue"))

        return scaling_score



        
    def monitor_service_loads(self):
        #Placeholder scale out logic
        # avg_cpu_usage= self.enviornment_interface.get_avg_system_load()

        # print(colored(f"Average system load: {avg_cpu_usage}", "yellow"))

        # if avg_cpu_usage > 120 and self.scale_out_count < self.max_scale_out_instances:
        #     print(colored(f"Scaling out!!", "green"))
        #     self.scale_out_instances()
        #     self.scale_out_count += 1

        # elif avg_cpu_usage > 70 and self.scale_out_count > 0:
        #     print(colored(f"Scaling out Down!!", "red"))
        #     self.enviornment_interface.stop_scaled_out_instances(1)
        scaling_score = self.scaling_out_decision()
        if scaling_score is None:
            return

        scaling_score = round(scaling_score)
        
        if scaling_score > 1 and self.scale_out_count < self.max_scale_out_instances:
            if self.scale_out_count + scaling_score < self.max_scale_out_instances:
                print(colored(f"[monitor_service_loads][scaling_score][scalingout] {scaling_score}", "green"))
                self.scale_out_instances(num=scaling_score)
                self.scale_out_count += scaling_score
            else:
                to_scaling = self.max_scale_out_instances - self.scale_out_count
                print(colored(f"[monitor_service_loads][scaling_score][scalingout][to_scaling] {to_scaling}", "green"))
                self.scale_out_instances(num=to_scaling)
                self.scale_out_count = self.max_scale_out_instances



        

    def watch(self):
        self.meta_data:dict = self.enviornment_interface.get_meta_data()

        if len(self.enviornment_interface.comm_for_agents) > 0:
            for comm in self.enviornment_interface.comm_for_agents:
                if comm["agent_id"] == self.agent_id:
                    if comm["type"] == "service_terminated":
                        service_identifier = comm["service_identifier"]
                        print(colored(f"Service {service_identifier} terminated", "red"))
                        self.scaled_out_termination_callback()
                        self.enviornment_interface.comm_for_agents.pop()

        instances:dict[str:dict] = self.meta_data["instances"]
        #check instance state
        for instance_identifier, instance_data in instances.items():
            if instance_data["status"] == 0 and instance_data.get("restart_initiated") == 0:
                print(colored(f"Service {instance_identifier} recovery request sent by agent", "yellow"))
                self.send_recover_service_request(instance_identifier)
        
        self.monitor_service_loads()

    def scale_out_instances(self,num = 1):
        self.enviornment_interface.add_new_instances(num)

    def scaled_out_termination_callback(self):
        self.scale_out_count -= 1