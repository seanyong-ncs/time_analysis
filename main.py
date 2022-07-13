import argparse
import pandas as pd
from occupancyanalyser import OccupancyAnalyser
from visualiser import Visualiser
import os


def save_analysis(results, save_dir, input_file, identifier, count_all):
    count_all_flag = "_count_all" if count_all else ""
    _, file_name = os.path.split(input_file)
    save_path = os.path.join(save_dir, file_name.split(".")[0] + f"_{identifier}{count_all_flag}.csv")
    print(save_path)
    results.to_csv(save_path ,index=False)
    print(f"{identifier} results saved to {save_path}")

def main():
    # Build argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="Input file/folder path", required=True)
    parser.add_argument("-g", "--granularity", help="Set the time slice window in minutes", type=int, default=60)
    parser.add_argument("-a", '--count_all', action='store_true')
    parser.add_argument("-v", "--verbose", help="Verbosely list operations", action="store_true")
    args = parser.parse_args()

    # Read csv file into raw_df
    raw_df = pd.read_csv(args.input_file)

    # Create analysis object and pass raw_df to constructor
    oa = OccupancyAnalyser(raw_df, granularity=args.granularity, count_all=args.count_all)
    
    # Create data visualiser object
    vs = Visualiser()

    # Get script path
    script_path, _ = os.path.split(os.path.abspath(__file__))
    
    # Define save path and create output folder if it doesn't exist
    save_dir = os.path.join(script_path, "output")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Generate analyses
    occupancy_time_results = oa.occupancy_time_analysis()
    max_occupancy_results = oa.max_occupancy_window_analysis()
    customer_staff_ratio_results = oa.customer_staff_ratio_analysis()

    vs.customer_staff_ratio_heatmap(customer_staff_ratio_results)

    # Save analyses to csv
    save_analysis(occupancy_time_results, save_dir, args.input_file, "occupancy_time", args.count_all)
    save_analysis(max_occupancy_results, save_dir, args.input_file, "max_occupancy", args.count_all)
    save_analysis(customer_staff_ratio_results, save_dir, args.input_file, "customer_staff_ratio", args.count_all)

    # Print analyses output if verbose flag is enabled
    if (args.verbose):
        print(occupancy_time_results)
        print(max_occupancy_results)
    

if __name__ == "__main__":
    main()