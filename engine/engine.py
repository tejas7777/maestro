from traffic.generator import TrafficGenerator
import json
import time
import numpy as np

class Engine():

    def __init__(self):
        self.traffic_generator = TrafficGenerator()
        self.path_to_artifact = 'engine/artifacts'
        self.time_policy = None

    def __fetch_time_policy(self) -> dict[str:dict]:
        with open(self.path_to_artifact+'/time.json', 'r') as f:
            self.time_policy = json.load(f)
            return self.time_policy


    def run(self):
        time_policy = self.__fetch_time_policy()

        if time_policy is None:
            return
        
        #Encapsulate everything with time
        for month in time_policy.keys():
            for day, day_data in time_policy[month].items():
                print("Day 1:", day)
                for hour_data in day_data["time_passage"]:
                    #Simulate minutes with time module using wait as one min equivalent real world second.
                    #From the hour data, get request and use poisson distribution to distribute the hourly requests through mins
                    hourly_requests = hour_data["num_req"]
                    
                    # Calculate lambda for Poisson distribution
                    lambda_per_minute = hourly_requests / 60
                    
                    # Distribute requests for each minute of the hour
                    requests_per_minute = np.random.poisson(lambda_per_minute, 60)
                    total_req = 0
                    for minute, req_count in enumerate(requests_per_minute, start=1):
                        # Simulate passing of each minute
                        print(f"Hour {hour_data['hour']} Minute {minute}: {req_count} requests")
                        time.sleep(1)  # Simulating 1 minute as 1 real-world second
                        total_req += req_count
                        
                        # Here you would handle each request simulation for this minute
                        # This is where you might call your traffic generator, for example
                        # self.traffic_generator.generate_requests(req_count)
                        requests = self.traffic_generator.generator(mode = "DETERMINISTIC", num = req_count )
                        print(f"Requests generated: {len(requests)}")

                    print(f"End of Hour {hour_data['hour']} Total {total_req} requests")
                    
                

            
        
        
    

    



