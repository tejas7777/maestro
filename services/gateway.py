from types.request import Request

class APIGateway():
    def __init__(self) -> None:
        pass

    def processRequest(self, request: Request) -> None:
        return self.routeRequest(request)

    def routeRequest(self,request: Request) -> bool:
        pass
