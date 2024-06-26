from intelligence.agents.recovery_agent import RecoveryAgent
from intelligence.agents.fuzzy_agent import FuzzyAgent
from intelligence.agents.predictive_agent import RecoveryAgentPredictive
from intelligence.agents.tsk_fuzzy_agent import RecoveryAgentTSK
from traffic.generator import TrafficGenerator
import json
import time
import numpy as np
from services.Chariot import Chariot
from services.instances import StandardInstance
from engine.meta.layer import MetaLayer
from engine.utils.helper import EngineHelper
from services.LoadBalancer import LoadBalancer
import math
from termcolor import colored
from engine.meta.layer import MetaLayer
from engine.utils.time_data import TimeData
from engine.meta.enviornment import Environment
from engine.api.agent_interface import EnviornmentAgentInterface
from services.database_service import DatabaseService
from engine.utils.statistics_collector import StatisticsCollector
from engine.utils.statistics_collector import AgentStatisticsCollector

'''
THIS IS THE MIND OF THE SYSTEM
'''


class Engine:

    def __init__(self):
        self.traffic_generator = TrafficGenerator()
        self.time_data = TimeData()
        self.path_to_artifact = 'engine/artifacts'
        self.time_policy = None
        self.config = self.__fetch_config()
        self.meta_layer = MetaLayer()
        self.engine_helper = EngineHelper(meta_layer=self.meta_layer, time_data=self.time_data)
        self.LoadBalancerObj = LoadBalancer()
        self.services = self.spawn_services(self.config["system"].get('initial_instance_count', 5))
        self.database_services = self.spawn_database_services(self.config["system"].get('initial_db_instance_count', 2))
        for service in self.services:
            self.LoadBalancerObj.register_service(service)  # Register once

        self.enviornment = Environment(
            services=self.services,
            load_balancer=self.LoadBalancerObj,
            meta_layer=self.meta_layer,
            time=self.time_data,
            database_services=self.database_services,
            config=self.config
        )

        unconnected_services = self.enviornment.assign_services_to_databases()

        if len(unconnected_services) > 0:
            #Need to add the list to events queue.
            self.enviornment.add_unconnected_services_to_events_queue(unconnected_services)

        self.resource_schedule = {}  # Scheduled resource releases
        self.task_queue = []

        self.agent_interface = EnviornmentAgentInterface(
            environment=self.enviornment,
        )

        self.statistics_collector = StatisticsCollector(meta_layer=self.meta_layer)
        self.agent_statistics_collector = AgentStatisticsCollector(meta_layer=self.meta_layer)

        self.agents = [
            RecoveryAgent(agent_id="recovery-agent", agent_type="recovery", enviornment_interface=self.agent_interface),
            RecoveryAgentPredictive(agent_id="recovery-agent", agent_type="recovery",
                                                      enviornment_interface=self.agent_interface),
            FuzzyAgent(agent_id="recovery-agent", agent_type="recovery", enviornment_interface=self.agent_interface),
        ]
        #Selecting Predicitve Agent
        self.recovery_agent = self.agents[1]

        
    def __fetch_time_policy(self) -> dict:
        with open(f"{self.path_to_artifact}/time.json", 'r') as f:
            self.time_policy = json.load(f)
            return self.time_policy

    def __fetch_config(self) -> dict[str, dict]:
        with open(f"{self.path_to_artifact}/config.json", 'r') as f:
            self.config = json.load(f)
            return self.config

    def spawn_services(self, num) -> list[StandardInstance]:
        services = []
        for i in range(num):
            new_service = StandardInstance(f'standard-instance-{i}', 500)
            services.append(new_service)
            self.engine_helper.add_intance_meta_data(new_service)

        return services

    def spawn_database_services(self, num) -> list[DatabaseService]:
        databse_services = []
        for i in range(num):
            new_service = DatabaseService(f'database-instance-{i}', max_connections=self.config["system"].get('db_max_connections', 5))
            databse_services.append(new_service)
            self.engine_helper.add_database_instance_meta_data(new_service)

        return databse_services


    #NOTE THIS FUNCTION IS DEPRECATED
    def schedule_resource_release(self, current_hour, current_minute, service, computation, request_id):
        release_minute = (current_minute + round(math.log1p(computation))) % 60
        release_hour = current_hour + (
                    (current_minute + round(math.log1p(computation))) // 60)  #Calculate which hour it falls into
        if (release_hour, release_minute) not in self.resource_schedule:
            self.resource_schedule[(release_hour, release_minute)] = []
        self.resource_schedule[(release_hour, release_minute)].append((service, computation, request_id))

    def schedule_resource_release_v2(self, current_hour, current_minute, service, computation, request_id):
        #THIS SOME TIMES THROWS DOMAIN ERROR !!!
        release_minute = round(math.log1p(computation))
        if release_minute == 0:
            release_minute = 1
        time_to_release = self.time_data.get_increment_minutes_str(release_minute, current_hour, self.time_data.day)

        task_obj = {
            "service": service,
            "computation": computation,
            "request_id": request_id,
            "type": "release_resources",
            "time": time_to_release
        }

        self.enviornment.environment_task_queue.append(task_obj)

    def schedule_database_resource_release(self, current_hour, database, disk_io, request_id):
        release_minute = round(math.log1p(disk_io))
        if release_minute == 0:
            release_minute = 1
        time_to_release = self.time_data.get_increment_minutes_str(release_minute, current_hour, self.time_data.day)

        task_obj = {
            "database": database,
            "disk_io": disk_io,
            "request_id": request_id,
            "type": "release_database_resources",
            "time": time_to_release
        }

        self.enviornment.environment_task_queue.append(task_obj)

    def simulate_minute(self, minute, req_count, current_hour):
        self.time_data.minuite = minute
        print(f"Minute {minute}: {req_count} requests")
        self.recovery_agent.watch()
        self.enviornment.update_environment()

        requests = self.traffic_generator.generator(mode="DETERMINISTIC", num=req_count)

        unprocessed_requests = 0

        for request in requests:
            service: StandardInstance = self.LoadBalancerObj.get_service_round_robin()
            
            if not service:
                print(f"No available service")
                break
            if service.can_handle_request(request=request):
                if request.disk_io_usage:
                    database = service.database_instance
                    if database:
                        if database.can_handle_disk_io(request.disk_io_usage):
                            database.handle_disk_io(request.disk_io_usage)
                            service.process_request(request=request)
                            #print(f"CPU USAGE {service.get_instance_identifier()}: {service.current_cpu} / {service.max_cpu}")
                            #print(f"Disk IO USAGE {database.get_instance_identifier()}: {database.current_disk_io} / {database.max_disk_io}")

                            self.schedule_resource_release_v2(service=service, current_minute=minute,
                                                              current_hour=current_hour,
                                                              computation=request.computation, request_id=request.id)
                            self.schedule_database_resource_release(current_hour, database, request.disk_io_usage,
                                                                    request.id)

                        else:
                            database.set_service_down()
                            unprocessed_requests += 1
                            print(colored(f"database {database.get_instance_identifier()} is DOWN", "red"))
                    else:
                        unprocessed_requests += 1
                        print(
                            colored(f"Service {service.get_instance_identifier()} not connected to a database instance",
                                    "red"))

                else:
                    service.process_request(request=request)
                    self.schedule_resource_release_v2(service=service, current_minute=minute, current_hour=current_hour,
                                                      computation=request.computation, request_id=request.id)
            else:
                unprocessed_requests += 1
                print(colored(f"Service {service.get_instance_identifier()} is DOWN", "red"))
                service.set_service_down()
                self.LoadBalancerObj.deregister_service(service)
                break

        self.enviornment.update_meta_data_after_every_minuite_v2({
            "unprocessed_requests_for_min": unprocessed_requests,
        })

        self.recovery_agent.update_observations(
            {"request_rate": req_count, "avg_cpu_usage": self.enviornment.get_avg_system_load_v2()})
        
        self.statistics_collector.collect_metrics(self.time_data.get_current_time_str())
        self.agent_statistics_collector.collect_kalman_actual_data(minuite=self.time_data.get_current_time_str(),
                                                                   actual=self.enviornment.get_avg_system_load_v2())

        time.sleep(1)

    def run_simulation_for_hour(self, hour_data):
        hourly_requests = hour_data['num_req']
        lambda_per_minute = hourly_requests / 60
        requests_per_minute = np.random.poisson(lambda_per_minute, 60)
        total_req = 0
        current_hour = hour_data['hour']
        self.time_data.hour = current_hour

        minutes_passed = 0

        for minute, req_count in enumerate(requests_per_minute, start=1):
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
