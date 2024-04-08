from types.request import Request
import random

class TrafficGenerator():
    
    def deterministicGenerator(self) -> list[Request]:
        '''
        Go through a CSV file which will act as a reference to
        Generate how many and what type of requests
        '''
        NotImplementedError("Not Implemented")

    def stochasticGenerator(self,mean,sd,time) -> list[Request]:
        '''
        A Gaussian Random Variable to generate
        How many and what type of requests
        '''
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        headers = [{'User-Agent': 'Browser'}]
        content_types = ['application/json']
        routes = ['/api/data', '/home', '/api/user']
        data_examples = ['{"key": "value"}']

        num_requests = int(random.gauss(mean, sd))

        method_index = int(random.gauss(mu=1.5, sigma=1)) % len(methods)

        generator_output = []
        

        


