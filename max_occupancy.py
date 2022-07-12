import argparse
from datetime import timedelta
import pandas as pd
import numpy as np

MINUTES = 60
SECONDS = 60

def initial_time(df):
    return df["firstSeen"].iloc[0].replace(hour=0, minute=0, second=0, microsecond=0)

# Transform data frame into relative time step and drop unnecessary rows
def prepreocess_df(df, count_all):
    # Drop rows if count_all
    if not count_all:
        df.drop(df.loc[df['crossLine']==False].index, inplace=True)

    # Convert string to dateTime object
    df["firstSeen"] = pd.to_datetime(df["firstSeen"])
    df["lastSeen"] = pd.to_datetime(df["lastSeen"])

    # Sort by firstSeen
    df.sort_values(by="firstSeen", ascending=True, inplace=True)
    
    # Convert dateTime to timedelta centered around 12am as start
    initial_dt = initial_time(df)

    df["fs_timeStep"] = (df["firstSeen"] - initial_dt).dt.total_seconds().astype(int)
    df["ls_timeStep"] = (df["lastSeen"] - initial_dt).dt.total_seconds().astype(int)

    df = df.drop(columns=["firstSeen", "lastSeen", "dwellTime", "engagementTime", "crossLine"])
   
    return df

def generate_time_list(df):
    max_time_step = 86400 # Seconds in a day
    results = np.zeros(max_time_step)

    for row in df.iterrows():
        rowList = np.zeros(max_time_step)
        # print(rowList)
        rowList[row[1][1]:row[1][2]] = 1
        results = rowList + results

    return results

def max_occupants_per_window(time_list, initial_dt, window):

    results = pd.DataFrame(columns=["timeStart", "timeEnd", "maxOccupants", "firstOccuranceTime"])

    for i in range(int(time_list.size/window)):
        # Define slice time steps and indices
        ts_start = i*window
        ts_stop = (i+1)*window-1 if (i+1)*window < time_list.size else time_list.size-1
        time_slice = time_list[ts_start:ts_stop]

        max_occupants = int(np.amax(time_slice))
        max_occupants_ts = np.where(time_list == np.amax(time_slice))[0] if max_occupants > 0 else np.NaN

        # Skip occurance search if no detection in time slice
        if ~np.isnan(max_occupants_ts).all():
            max_occupants_ts = max_occupants_ts[(max_occupants_ts > ts_start)]

        # Convert relative timestep to dateTime object
        start_dt = initial_dt + timedelta(seconds=i*window)
        end_dt = initial_dt + timedelta(seconds=ts_stop)
        time_of_occurance = initial_dt + timedelta(seconds=max_occupants_ts[0].item()) if max_occupants > 0 else np.NaN
        
        # Format a dataframe with one row to append to the end of the temp results frame
        newRow = {"timeStart": [start_dt], "timeEnd": [end_dt], "maxOccupants": [max_occupants], "firstOccuranceTime": [time_of_occurance]}
        results = pd.concat([results, pd.DataFrame(newRow)], ignore_index=True)

    
    return results


def generate_analysis(time_list, raw_df, granularity):
    initial_dt = initial_time(raw_df)
    return max_occupants_per_window(time_list, initial_dt, granularity*SECONDS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="Input file path", required=True)
    parser.add_argument("-o", "--output_file", help="Output file path", default="")
    parser.add_argument("-g", "--granularity", help="Set the time slice window in minutes", type=int, default=60)
    parser.add_argument("-a", '--count_all', action='store_true')
    parser.add_argument("-v", "--verbose", help="Verbosely list operations", action="store_true")
    
    args = parser.parse_args()

    raw_df = pd.read_csv(args.input_file)
    
    df = prepreocess_df(raw_df, args.count_all)

    time_list = generate_time_list(df)
    results = generate_analysis(time_list, raw_df, args.granularity)

    output_file = args.output_file if args.output_file != "" else args.input_file.split(".")[0] + "_max_occupancy.csv"
    results.to_csv(output_file ,index=False)
    
    print(f"Results saved to {output_file}")

    if (args.verbose):
        print(results)
    

if __name__ == "__main__":
    main()