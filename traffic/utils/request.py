class Request():
    def __init__(self,method,header,content_type,route,data,computation = None, time = None) -> None:
        self.method = method
        self.header = header
        self.content_type = content_type
        self.route = route
        self.data = data
        self.time = time
        self.computation = computation