import argparse
import pandas as pd
from occupancyanalyser import OccupancyAnalyser
from visualiser import Visualiser
import os

import numpy as np


def save_analysis(results, save_dir, input_file, identifier, count_all):
    count_all_flag = "_count_all" if count_all else ""
    _, file_name = os.path.split(input_file)
    save_path = os.path.join(save_dir, file_name.split(".")[0] + f"_{identifier}{count_all_flag}.csv")
    results.to_csv(save_path ,index=False)
    # print(f"{identifier} results saved to {save_path}")

def generate_occupancy_analysis(df_path, args):
    # Read csv file into raw_df
    raw_df = pd.read_csv(df_path)

    # Create analysis object and pass raw_df to constructor
    oa = OccupancyAnalyser(raw_df, granularity=args.granularity, count_all=args.count_all)
    
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
    csr_treshold_results = oa.customer_staff_ratio_treshold_analysis()

    # Save analyses to csv
    save_analysis(occupancy_time_results, save_dir, df_path, "occupancy_time", args.count_all)
    save_analysis(max_occupancy_results, save_dir, df_path, "max_occupancy", args.count_all)
    save_analysis(customer_staff_ratio_results, save_dir, df_path, "customer_staff_ratio", args.count_all)
    save_analysis(csr_treshold_results, save_dir, df_path, "customer_staff_ratio_threshold", args.count_all)

    # Print analyses output if verbose flag is enabled
    if (args.verbose):
        print(occupancy_time_results)
        print(max_occupancy_results)

    return occupancy_time_results, max_occupancy_results, customer_staff_ratio_results

def main():
    # Build argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", help="Input file/folder path", required=True)
    parser.add_argument("-g", "--granularity", help="Set the time slice window in minutes", type=int, default=60)
    parser.add_argument("-a", '--count_all', action='store_true')
    parser.add_argument("-v", "--verbose", help="Verbosely list operations", action="store_true")
    args = parser.parse_args()

    if not os.path.isdir(args.input_path):
        generate_occupancy_analysis(args.input_path, args)
        print("Only 1 file specified. Skipping over heatmap generation")
    else:
        results = [generate_occupancy_analysis(os.path.join(args.input_path, f), args) 
                    for f in sorted(os.listdir(args.input_path)) if f.endswith(".csv")]
        # Transpose result array
        results = list(zip(*results)) 
    
        # Create data visualiser object
        vs = Visualiser()

        mo_list = results[1]
        csr_list = results[2]
        vs.customer_staff_ratio_heatmap(csr_list)
        vs.max_occupancy_heatmap(mo_list)

    print("Done!")
    
    

if __name__ == "__main__":
    main()