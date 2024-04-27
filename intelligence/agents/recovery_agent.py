from termcolor import colored
from engine.api.agent_interface import EnviornmentAgentInterface

class RecoveryAgent:
    def __init__(self, agent_id: str, agent_type: str, enviornment_interface: EnviornmentAgentInterface):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.enviornment_interface = enviornment_interface

    def send_recover_service_request(self,service_identifier: str):
        self.enviornment_interface.restart_service(service_identifier, 2)
        
    def monitor_service_loads(self):
        pass

    def watch(self):
        meta_data:dict = self.enviornment_interface.get_meta_data()

        instances:dict[str:dict] = meta_data["instances"]
        #check instance state
        for instance_identifier, instance_data in instances.items():
            if instance_data["status"] == 0 and instance_data.get("restart_initiated") == 0:
                print(colored(f"Service {instance_identifier} recovery request sent by agent", "yellow"))
                self.send_recover_service_request(instance_identifier)
            else:
                self.monitor_service_loads()

            
            


        

        
