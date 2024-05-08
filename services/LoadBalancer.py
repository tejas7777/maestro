import numpy as np
from intelligence.kalman_filter import KalmanFilter

class LoadBalancer:
    def __init__(self):
        self.services = []
        self.index = 0  # for round-robin strategy
        self.kalman_filter = self.init_klaman_filter()


    def init_klaman_filter(self):
        # Kalman Filter Initialization
        F = np.array([[1]])  # State transition matrix, assuming simple system dynamics
        Q = np.array([[1e-5]])  # Process noise covariance, small value assuming low process noise
        H = np.array([[1]])  # Observation matrix
        R = np.array([[1e-2]])  # Measurement noise covariance, adjust based on actual observation noise
        x0 = np.array([[10]])  # Initial state estimate, perhaps an average of past data
        P0 = np.array([[1]])  # Initial covariance estimate, somewhat arbitrary

        return KalmanFilter(F=F, Q=Q, H=H, R=R, x0=x0, P0=P0, tuning_period=15)

    def register_service(self, *args):
        for arg in args:
            self.services.append(arg)

    def get_service_round_robin(self):
        # Simple round-robin load balancing, returns one service at a time
        if not self.services:
            return None
        service = self.services[self.index]
        self.index = (self.index + 1) % len(self.services)
        return service

    def get_service_least_cpu(self):
        # Get the service with the least current CPU usage that is still operational
        available_services = [s for s in self.services if s.state != 0]
        if not available_services:
            return None
        # Return one service with the minimum CPU usage
        return min(available_services, key=lambda x: x.current_cpu)

    def deregister_service(self, service):
        # Remove a service from the list, if necessary
        if service in self.services:
            self.services.remove(service)

    def predict_requests(self):
        # Use the Kalman Filter to predict the next state (number of requests)
        predicted_requests = self.kalman_filter.predict()
        return predicted_requests

    def update_kalman_filter(self, actual_requests):
        # Update the Kalman Filter with the actual observed number of requests
        self.kalman_filter.update(np.array([[actual_requests]]))

    def distribute_load(self, predicted_requests):
        # Distribute the load based on predicted requests
        total_capacity = sum(service.capacity for service in self.services)
        load_distribution = {service.identifier: (predicted_requests[0][0] * service.capacity / total_capacity)
                             for service in self.services}
        return load_distribution

    def handle_requests(self, current_minute, actual_requests):
        predicted_requests = self.predict_requests()
        load_distribution = self.distribute_load(predicted_requests)

        # Assign requests to services based on the distribution
        for service in self.services:
            if service.identifier in load_distribution:
                service.handle_requests(load_distribution[service.identifier], current_minute)

        # After handling requests, update the Kalman Filter with the actual number of requests
        self.update_kalman_filter(actual_requests)



    def distribute_load_based_on_prediction(self, current_minute):
        predicted_requests = self.predict_requests()  # Get predicted number of requests
        total_capacity = sum(service.capacity for service in self.services if service.state != 0)
        
        # Calculate the number of requests each service should handle based on capacity and prediction
        for service in self.services:
            if service.state != 0:  # Ensure the service is operational
                allocated_requests = int((predicted_requests[0][0] * service.capacity) / total_capacity)
                service.handle_requests(allocated_requests, current_minute)
                print(f"Allocated {allocated_requests} requests to {service.get_instance_identifier()} at minute {current_minute}")
                
        # Update the Kalman Filter with the actual number of requests received
        actual_requests = sum(service.processed_requests for service in self.services)  # Assuming each service tracks its processed requests
        self.update_kalman_filter(actual_requests)

    def get_service_least_connections(self):
        # Returns the service with the minimum number of active connections
        if not self.services:
            return None
        # Assuming each service has a method `get_active_connection_count()` that returns the current number of connections
        return min(self.services, key=lambda service: service.request_processed if service.state != 0 else float('inf'))