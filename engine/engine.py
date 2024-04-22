from traffic.generator import TrafficGenerator
import json
import time
import numpy as np
from services.Chariot import Chariot
from engine.meta.layer import MetaLayer
from engine.utils.helper import EngineHelper
import random
from services.LoadBalancer import LoadBalancer
import threading
import math

class Engine:

    def __init__(self):
        self.traffic_generator = TrafficGenerator()
        self.path_to_artifact = 'engine/artifacts'
        self.time_policy = None
        self.MetaLayerObj = MetaLayer()
        self.EngineHelperObj = EngineHelper(MetaLayerObj=self.MetaLayerObj)
        self.LoadBalancerObj = LoadBalancer()
        self.services = self.spawn_services()
        for service in self.services:
            self.LoadBalancerObj.register_service(service)  # Register once

    def __fetch_time_policy(self) -> dict:
        with open(f"{self.path_to_artifact}/time.json", 'r') as f:
            self.time_policy = json.load(f)
            return self.time_policy
        
    def spawn_services(self):
        return [Chariot(f'chariot-instance-{i}', 500) for i in range(1)]

    def simulate_minute(self, minute, req_count):
        print(f"Minute {minute}: {req_count} requests")
        requests = self.traffic_generator.generator(mode="DETERMINISTIC", num=req_count)
        service = self.LoadBalancerObj.get_service_least_cpu()
        if not service:
            print("No available service to handle the request")
            return
        
        for request in requests:
            if service.can_handle_request(request=request):
                service.process_request(request=request)
                print(f"CPU USAGE: {service.current_cpu} / {service.max_cpu}")

                #Send for reseource release
                self.schedule_resource_release(service, computation=request.computation, request_id=request.id)
            else:
                print(f"Service {service.get_instance_identifier()} is DOWN")
                self.LoadBalancerObj.deregister_service(service)
                #break 
            time.sleep(1)  # Simulate real-time minute passing

    def run_simulation_for_hour(self, hour_data):
        hourly_requests = hour_data['num_req']
        lambda_per_minute = hourly_requests / 60
        requests_per_minute = np.random.poisson(lambda_per_minute, 60)
        # services = self.services
        # self.LoadBalancerObj.register_service(*services)
        total_req = 0

        for minute, req_count in enumerate(requests_per_minute, start=1):
            self.simulate_minute(minute, req_count)
            total_req += req_count
        print(f"End of Hour {hour_data['hour']} Total {total_req} requests")

    def schedule_resource_release(self, service, computation, request_id):
        def release_resources():
            delay = round(math.log1p(computation))
        
            time.sleep(delay if delay >=1 else 1)  # Simulate resource hold for 1 simulated minute
      
            if service.state == 0:
                print(f"Service {service.identifier} is down. No resource release.")
                return #Service is already down, don't bother.
            
            service.release_resources(computation)
            print(f"Released resources for service {service.identifier} for request {request_id}. Current CPU: {service.current_cpu}")

        thread = threading.Thread(target=release_resources)
        thread.start()


    def run(self):
        time_policy = self.__fetch_time_policy()
        if time_policy is None:
            return

        for month in time_policy.keys():
            for day, day_data in time_policy[month].items():
                print(f"Day {day}")
                for hour_data in day_data['time_passage']:
                    self.run_simulation_for_hour(hour_data)
                    



