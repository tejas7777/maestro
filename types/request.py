class Request():

    def __init__(self,method,header,content_type,route,data, time = None) -> None:
        self.method = method
        self.header = header
        self.content_type = content_type
        self.route = route
        self.data = data
        self.time = time

