from traffic.utils.request import Request
import random
import string

class TrafficGenerator():

    request_params = {
        "methods" : ['GET', 'POST', 'PUT', 'DELETE'],
        "headers" : [{'User-Agent': 'Browser'}],
        "content_types" : ['application/json'],
        "routes" : ['/api/data', '/home', '/api/user'],
        "data_examples" : ['{"key": "value"}']
    }

    computation_units = {
        'GET': [20, 5],  # Example: mean=20, sd=5
        'POST': [40, 10],
        'PUT': [50, 7],
        'DELETE': [15, 4]
    }

    
    def deterministic(self, params) -> list[Request]:
        '''
        Go through a CSV file which will act as a reference to
        Generate how many and what type of requests
        '''
        num_requests = params.get("num")

        output_list = []
        
        for __ in range(num_requests):
            #Select method based on Gaussian distribution
            method_index = int(random.gauss(mu=1.5, sigma=1)) % len(self.request_params["methods"])
            method = self.request_params["methods"][method_index]
            
            #Determine computation units for the selected method
            mean, sd = self.computation_units[method]
            computation = int(random.gauss(mean, sd))

            processing_factor = 0.075  # This factor determines the conversion rate
            processing_time = computation * processing_factor
   
            request = Request(
                method=method,
                header=random.choice(self.request_params["headers"]),
                content_type=random.choice(self.request_params["content_types"]),
                route=random.choice(self.request_params["routes"]),
                data=random.choice(self.request_params["data_examples"]),
                computation=computation,
                time= processing_time,
                id=''.join(random.choice(string.ascii_lowercase) for i in range(5))
            )
            output_list.append(request)

        return output_list




    def stochastic(self,params) -> list[Request]:
        '''
        A Gaussian Random Variable to generate
        How many and what type of requests
        '''

        num_requests = int(random.gauss(params.get("mean"), params.get("sd")))
        method_index = int(random.gauss(mu=1.5, sigma=1)) % len(self.request_params["methods"])


    def generator(self, mode, **params):

        match mode:
            case "DETERMINISTIC":
                return self.deterministic(params)
            case "STOCHASTIC":
                return self.stochastic(params)
            case __:
                return None

        
        

        


