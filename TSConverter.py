from datetime import timedelta
import pandas as pd

class TimeStepConverter:
    def __init__(self):
        self.initial_dt = None

    def set_initial_dt(self, df):
        df["firstSeen"] = pd.to_datetime(df["firstSeen"])
        self.initial_dt = df["firstSeen"].iloc[0].replace(hour=0, minute=0, second=0, microsecond=0)

    def dateTime_to_timeStep(self, dateTime):
        return (dateTime - self.initial_dt).dt.total_seconds().astype(int)

    def timeStep_to_dateTime(self, timeStep):
        return self.initial_dt + timedelta(seconds=timeStep)