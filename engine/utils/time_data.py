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
    
    def get_current_time_str(self):
        return "d:"+str(self.day)+"h:"+str(self.hour)+"m:"+str(self.minuite)
    
    def get_increment_minutes_str(self, minutes, hour, day):
        minuite = self.minuite + minutes

        if minuite >= 60:
            hour += minuite // 60
            minuite %= 60
            if hour >= 24:
                day += hour // 24
                hour %= 24
        
        return "d:"+str(day)+"h:"+str(hour)+"m:"+str(minuite)