import argparse
from datetime import timedelta
import pandas as pd
import numpy as np
from TSConverter import TimeStepConverter

tsc = TimeStepConverter()

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
    
    # Replace dateTime with relative timeStep
    df["fs_timeStep"] = tsc.dateTime_to_timeStep(df["firstSeen"])
    df["ls_timeStep"] = tsc.dateTime_to_timeStep(df["lastSeen"])

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

    return results.astype(int)

def generate_window_analysis(time_list, granularity):

    window = granularity * 60

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
        start_dt = tsc.timeStep_to_dateTime(ts_start)
        end_dt = tsc.timeStep_to_dateTime(ts_stop)
        time_of_occurance = tsc.timeStep_to_dateTime(max_occupants_ts[0].item()) if max_occupants > 0 else np.NaN
        
        # Format a dataframe with one row to append to the end of the temp results frame
        newRow = {"timeStart": [start_dt], "timeEnd": [end_dt], "maxOccupants": [max_occupants], "firstOccuranceTime": [time_of_occurance]}
        results = pd.concat([results, pd.DataFrame(newRow)], ignore_index=True)

    
    return results

def generate_occupancy_run_list(time_list):
    last_occupancy = time_list[0]
    run_length = 1

    run_list = []
    for current_occupancy in time_list[1:]:
        if current_occupancy == last_occupancy:
            run_length += 1
        else:
            run_list.append((last_occupancy, run_length))
            run_length = 1
            last_occupancy = current_occupancy
    
    return run_list

def generate_occupancy_analysis(occupancy_run_list):
    results = pd.DataFrame(columns=["occupants", "timeStart", "timeEnd", "duration"])
    run_index = 0

    for run in occupancy_run_list:
        start_dt = tsc.timeStep_to_dateTime(run_index)
        end_dt = tsc.timeStep_to_dateTime(run_index + run[1] - 1)
        run_index += run[1]
        newRow = {"occupants": [run[0]], "timeStart": [start_dt], "timeEnd": [end_dt], "duration": [run[1]]}
        results = pd.concat([results, pd.DataFrame(newRow)], ignore_index=True)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="Input file path", required=True)
    parser.add_argument("-g", "--granularity", help="Set the time slice window in minutes", type=int, default=60)
    parser.add_argument("-a", '--count_all', action='store_true')
    parser.add_argument("-v", "--verbose", help="Verbosely list operations", action="store_true")
    
    args = parser.parse_args()

    raw_df = pd.read_csv(args.input_file)

    tsc.set_initial_dt(raw_df)
    
    df = prepreocess_df(raw_df, args.count_all)

    time_list = generate_time_list(df)

    count_all_flag = "_count_all" if args.count_all else ""

    occupancy_run_list = generate_occupancy_run_list(time_list)
    occupancy_time_results = generate_occupancy_analysis(occupancy_run_list)
    occupancy_time_output_file = args.input_file.split(".")[0] + f"_occupancy_time{count_all_flag}.csv"
    occupancy_time_results.to_csv(occupancy_time_output_file ,index=False)

    max_occupancy_results = generate_window_analysis(time_list, args.granularity)
    max_occupancy_output_file = args.input_file.split(".")[0] + f"_max_occupancy{count_all_flag}.csv"
    max_occupancy_results.to_csv(max_occupancy_output_file ,index=False)


    print(f"Occupancy-Time Results saved to {occupancy_time_output_file}")
    print(f"Max Occupancy Results saved to {max_occupancy_output_file}")

    if (args.verbose):
        print(occupancy_time_results)
        print(max_occupancy_results)
    

if __name__ == "__main__":
    main()