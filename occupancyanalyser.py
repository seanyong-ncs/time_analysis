from cmath import isnan
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

        # MOWA results are saved as a variable for analysis built on top
        self.mowa = None # max_occupancy_window_analysis

        # Convert firstSeen to dateTime and set initial_dt to start of day
        self.initial_dt = pd.to_datetime(df["firstSeen"]).iloc[0].replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Preprocess raw_df
        self.clean_df = self.preprocess_df()

        # Generate the time list
        self.time_list = self.generate_time_list()

    # Returns a pandas dataframe containing the results of max occupancy per window analysis
    def max_occupancy_window_analysis(self):

        # Blank dataframe to hold the results
        results = pd.DataFrame(columns=["timeStart", "timeEnd", "maxOccupants", "firstOccuranceTime", "interval"])

        for i, time_slice in enumerate(np.split(self.time_list, int(self.time_list.size/self.granularity_s))):

            max_occupants = int(np.amax(time_slice))
            max_occupants_ts = np.where(self.time_list == max_occupants)[0]
            NaNSet = lambda x: x if max_occupants > 0 else np.NaN
            ts = lambda x: self.tsdt((i + x)*self.granularity_s)
            
            # Format a dataframe with one row to append to the end of the temp results frame
            newRow = {"timeStart": [ts(0)], "timeEnd": [ts(1)], 
                      "maxOccupants": [max_occupants], "firstOccuranceTime": [NaNSet(self.tsdt(max_occupants_ts[0].item()))], 
                      "interval": [NaNSet(max_occupants_ts.size)]}

            results = pd.concat([results, pd.DataFrame(newRow)], ignore_index=True)

        return results
   

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

    def customer_staff_ratio_treshold_analysis(self, staff = 3, csr_threshold = 3):
        # Blank dataframe to hold the results
        results = pd.DataFrame(columns=["timeStart", "timeEnd", "csrThreshold", "interval"])
        for i, time_slice in enumerate(np.split(self.time_list, int(self.time_list.size/self.granularity_s))):

            # Time step to dateTime at index x
            ts = lambda x: self.tsdt((i + x)*self.granularity_s)

            # Count the number of seconds where the CSR threshold was exceeded
            treshold_interval = time_slice[(time_slice / staff) >= csr_threshold].size

            # Format a dataframe with one row to append to the end of the temp results frame
            newRow = {"timeStart": [ts(0)], "timeEnd": [ts(1)], "csrThreshold": [csr_threshold], "interval": [treshold_interval]}
            results = pd.concat([results, pd.DataFrame(newRow)], ignore_index=True)
        
        return results

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