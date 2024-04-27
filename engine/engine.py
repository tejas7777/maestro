from intelligence.agents.recovery_agent import RecoveryAgent
from traffic.generator import TrafficGenerator
import json
import time
import numpy as np
from services.Chariot import Chariot
from services.instances import StandardInstance
from engine.meta.layer import MetaLayer
from engine.utils.helper import EngineHelper
import random
from services.LoadBalancer import LoadBalancer
import math
from intelligence.kalman_filter import KalmanFilter
from termcolor import colored
from engine.meta.layer import MetaLayer
from engine.utils.time_data import TimeData
from engine.meta.enviornment import Environment
from engine.api.agent_interface import EnviornmentAgentInterface
from services.database_service import DatabaseService


class Engine:

    def __init__(self):
        self.traffic_generator = TrafficGenerator()
        self.time_data = TimeData()
        self.path_to_artifact = 'engine/artifacts'
        self.time_policy = None
        self.meta_layer = MetaLayer()
        self.engine_helper = EngineHelper(meta_layer=self.meta_layer,time_data=self.time_data)
        self.LoadBalancerObj = LoadBalancer()
        self.services = self.spawn_services(5)
        self.spawn_databse_services(2)
        for service in self.services:
            self.LoadBalancerObj.register_service(service)  # Register once
        self.resource_schedule = {}  # Scheduled resource releases

        self.task_queue = []

        self.enviornment = Environment(
            services=self.services,
            load_balancer=self.LoadBalancerObj,
            meta_layer=self.meta_layer,
            time=self.time_data

        )
        
        self.agent_interface = EnviornmentAgentInterface(
            environment=self.enviornment,
        )

        self.recovery_agent = RecoveryAgent(agent_id="recovery-agent", agent_type="recovery", enviornment_interface=self.agent_interface)


    def __fetch_time_policy(self) -> dict:
        with open(f"{self.path_to_artifact}/time.json", 'r') as f:
            self.time_policy = json.load(f)
            return self.time_policy
        
    def spawn_services(self,num):
        services = []
        for i in range(num):
            new_service = StandardInstance(f'standard-instance-{i}', 500)
            services.append(new_service)
            self.engine_helper.add_intance_meta_data(new_service)

        return services
    
    def spawn_databse_services(self,num):
        services = []
        for i in range(num):
            new_service = StandardInstance(f'database-instance-{i}', 500)
            services.append(new_service)
            self.engine_helper.add_intance_meta_data(new_service)

        return services
        
    
    def schedule_resource_release(self, current_hour, current_minute, service, computation, request_id):
        release_minute = (current_minute + round(math.log1p(computation))) % 60
        release_hour = current_hour + ((current_minute + round(math.log1p(computation))) // 60)  # Calculate which hour it falls into
        if (release_hour, release_minute) not in self.resource_schedule:
            self.resource_schedule[(release_hour, release_minute)] = []
        self.resource_schedule[(release_hour, release_minute)].append((service, computation, request_id))

    def schedule_resource_release_v2(self, current_hour, current_minute, service, computation, request_id):
        release_minute =  round(math.log1p(computation))
        time_to_release = self.time_data.get_increment_minutes_str(release_minute, current_hour, self.time_data.day)

        task_obj = {
            "service": service,
            "computation": computation,
            "request_id": request_id,
            "type": "release_resources",
            "time": time_to_release
        }

        self.enviornment.environment_task_queue.append(task_obj)
    

    def simulate_minute(self, minute, req_count, current_hour):
        self.time_data.minuite = minute
        # print(f"TEST Meta Layer: {self.meta_layer.get_data()}")
        print(f"Minute {minute}: {req_count} requests")
        self.recovery_agent.watch()
        self.enviornment.update_environment()
        
        requests = self.traffic_generator.generator(mode="DETERMINISTIC", num=req_count)
        service: StandardInstance = self.LoadBalancerObj.get_service_least_cpu()

        for request in requests:
            if not service:
                print(f"No available service")
                break
            if service.can_handle_request(request=request):
                service.process_request(request=request)
                print(f"CPU USAGE {service.get_instance_identifier()}: {service.current_cpu} / {service.max_cpu}")
                #Send for reseource release
                self.schedule_resource_release_v2(service=service, current_minute= minute, current_hour=current_hour, computation=request.computation, request_id=request.id)
            else:
                print(colored(f"Service {service.get_instance_identifier()} is DOWN","red"))
                service.set_service_down()
                self.LoadBalancerObj.deregister_service(service)
                break
        self.engine_helper.update_meta_data_after_every_minuite(
            data = {
                "instances": self.services
            }
        )

        time.sleep(1)  # Simulate real-time minute passing
        self.engine_helper.update_time_in_meta_layer()

    def run_simulation_for_hour(self, hour_data):
        hourly_requests = hour_data['num_req']
        lambda_per_minute = hourly_requests / 60
        requests_per_minute = np.random.poisson(lambda_per_minute, 60)
        total_req = 0
        current_hour = hour_data['hour']
        self.time_data.hour = current_hour
        
        minutes_passed = 0

        for minute, req_count in enumerate(requests_per_minute, start=1):
            #schedule_key = (current_hour, minute)

            # if schedule_key in self.resource_schedule:
            #     for service, computation, request_id in self.resource_schedule.pop(schedule_key, []):
            #         if service.state == 0:
            #             pass
            #         else:
            #             service.release_resources(computation)
            #             print(f"Released resources for service {service.identifier} for request {request_id}. Current CPU: {service.current_cpu}")

            
            self.simulate_minute(minute, req_count, current_hour)
            total_req += req_count
            minutes_passed += 1

        print(f"End of Hour {hour_data['hour']} Total {total_req} requests")


    def run(self):
        time_policy = self.__fetch_time_policy()
        if time_policy is None:
            return
        for month in time_policy.keys():
            for day, day_data in time_policy[month].items():
                print(f"Day {day}")
                self.time_data.day = day
                for hour_data in day_data['time_passage']:
                    self.run_simulation_for_hour(hour_data)
                    



