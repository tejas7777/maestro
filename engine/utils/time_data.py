class TimeData:
    def __init__(self):
        self.day = 1
        self.hour = 0
        self.minuite = 1

    def update_time(self,day,hour,munuite):
        self.day = day
        self.hour = hour
        self.minuite = munuite

    def get_current_time(self):
        return {
            "day": self.day,
            "hour": self.hour,
            "minuite": self.minuite
        }
