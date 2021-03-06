import pandas as pd
import numpy as np
from datetime import timedelta

class OccupancyAnalyser:
    
    # Consts
    max_time_step = 86400 # Seconds in a day

    def __init__(self, df, count_all, granularity):
        # Set class variables
        self.raw_df = df
        self.count_all = count_all
        self.granularity_s = granularity * 60 # Convert from minutes to seconds

        # MCWA results are saved as a variable for analysis built on top
        self.mcwa = None # max_occupancy_window_analysis

        # Convert firstSeen to dateTime and set initial_dt to start of day
        self.initial_dt = pd.to_datetime(df["firstSeen"]).iloc[0].replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Preprocess raw_df
        self.clean_df = self.preprocess_df()

        # Generate the time list
        self.time_list = self.generate_time_list()

    # Returns a pandas dataframe containing the results of max occupancy per window analysis
    def max_occupancy_window_analysis(self):

        if self.mcwa is None:
            # Blank dataframe to hold the results
            results = pd.DataFrame(columns=["timeStart", "timeEnd", "maxOccupants", "firstOccuranceTime"])

            for i in range(int(self.time_list.size/self.granularity_s)):
                # Define slice time steps and indices
                ts_start = i*self.granularity_s # ts stands for timeStep
                ts_stop = (i+1)*self.granularity_s-1 if (i+1)*self.granularity_s < self.time_list.size else self.time_list.size-1
                time_slice = self.time_list[ts_start:ts_stop]

                max_occupants = int(np.amax(time_slice))
                max_occupants_ts = np.where(self.time_list == np.amax(time_slice))[0] if max_occupants > 0 else np.NaN

                # Skip occurance search if no detection in time slice
                if ~np.isnan(max_occupants_ts).all():
                    max_occupants_ts = max_occupants_ts[(max_occupants_ts > ts_start)]

                # Convert relative timestep to dateTime object
                start_dt = self.tsdt(ts_start)
                end_dt = self.tsdt(ts_stop)
                time_of_occurance = self.tsdt(max_occupants_ts[0].item()) if max_occupants > 0 else np.NaN
                
                # Format a dataframe with one row to append to the end of the temp results frame
                newRow = {"timeStart": [start_dt], "timeEnd": [end_dt], "maxOccupants": [max_occupants], "firstOccuranceTime": [time_of_occurance]}
                results = pd.concat([results, pd.DataFrame(newRow)], ignore_index=True)

            self.mcwa = results

        return self.mcwa

    def occupancy_time_analysis(self):
        # Initial case
        last_occupancy = self.time_list[0]
        
        run_length = 1
        run_list = []
        
        for current_occupancy in self.time_list[1:]:
            if current_occupancy == last_occupancy:
                run_length += 1
            else:
                run_list.append((last_occupancy, run_length))
                run_length = 1
                last_occupancy = current_occupancy

        run_index = 0
        results = pd.DataFrame(columns=["occupants", "timeStart", "timeEnd", "duration"])
        for r in run_list:
            # r[0]: occupancy, r[1]: run_length
            run_index += r[1]
            newRow = {"occupants": [r[0]], "timeStart": [self.tsdt(run_index)], 
            "timeEnd": [self.tsdt(run_index + r[1])], "duration": [r[1]]}
            results = pd.concat([results, pd.DataFrame(newRow)], ignore_index=True)

        return results

    def customer_staff_ratio_analysis(self, staff = 3):
        df = self.max_occupancy_window_analysis().copy(deep=True)
        df['customerStaffRatio'] = df['maxOccupants'].astype(float).div(staff).round(2)
        df = df.drop(columns=["firstOccuranceTime", 'maxOccupants'])
        return df


    # ------------Support functions-------------

    # Preprocess DF
    def preprocess_df(self):
        # Drop rows if count_all
        if not self.count_all:
            self.raw_df.drop(self.raw_df.loc[self.raw_df['crossLine']==False].index, inplace=True)

        # Convert string to dateTime object
        self.raw_df["firstSeen"] = pd.to_datetime(self.raw_df["firstSeen"])
        self.raw_df["lastSeen"] = pd.to_datetime(self.raw_df["lastSeen"])

        # Sort by firstSeen
        self.raw_df.sort_values(by="firstSeen", ascending=True, inplace=True)
        
        # Replace dateTime with relative timeStep
        self.raw_df["fs_timeStep"] = self.dtts(self.raw_df["firstSeen"])
        self.raw_df["ls_timeStep"] = self.dtts(self.raw_df["lastSeen"])

        # Drop unused columns
        self.raw_df = self.raw_df.drop(columns=["firstSeen", "lastSeen", "dwellTime", "engagementTime", "crossLine"])
    
        return self.raw_df
    
    # Create time list from clean_df
    def generate_time_list(self):
        results = np.zeros(OccupancyAnalyser.max_time_step)
        for row in self.clean_df.iterrows():
            rowList = np.zeros(OccupancyAnalyser.max_time_step)
            rowList[row[1][1]:row[1][2]] = 1
            results = rowList + results
        return results.astype(int)

    # Time step utilities
    
    # dateTime to timeStep
    def dtts(self, dateTime):
        return (dateTime - self.initial_dt).dt.total_seconds().astype(int)

    # timeStep to dateTime
    def tsdt(self, timeStep):
        return self.initial_dt + timedelta(seconds=timeStep)