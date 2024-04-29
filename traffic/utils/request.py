class Request():
    def __init__(self,method,header,content_type,route,data,computation = None, time = None,id=None, disk_io_usage = None) -> None:
        self.id = id
        self.method = method
        self.header = header
        self.content_type = content_type
        self.route = route
        self.data = data
        self.time = time
        self.computation = computation
        self.disk_io_usage = disk_io_usage