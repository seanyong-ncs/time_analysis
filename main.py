import argparse
import pandas as pd
from occupancyanalyser import OccupancyAnalyser
from visualiser import Visualiser

def save_analysis(results, input_file, identifier, count_all):
    count_all_flag = "_count_all" if count_all else ""
    file_name = input_file.split(".")[-2] + f"_{identifier}{count_all_flag}.csv"
    results.to_csv(file_name ,index=False)
    print(f"{identifier} results saved to {file_name}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="Input file path", required=True)
    parser.add_argument("-g", "--granularity", help="Set the time slice window in minutes", type=int, default=60)
    parser.add_argument("-a", '--count_all', action='store_true')
    parser.add_argument("-v", "--verbose", help="Verbosely list operations", action="store_true")
    
    args = parser.parse_args()

    raw_df = pd.read_csv(args.input_file)

    oa = OccupancyAnalyser(raw_df, granularity=args.granularity, count_all=args.count_all)
    vs = Visualiser()

    occupancy_time_results = oa.occupancy_time_analysis()
    max_occupancy_results = oa.max_occupancy_window_analysis()
    customer_staff_ratio_results = oa.customer_staff_ratio_analysis()

    vs.customer_staff_ratio_heatmap(customer_staff_ratio_results)

    save_analysis(occupancy_time_results, args.input_file, "occupancy_time", args.count_all)
    save_analysis(max_occupancy_results, args.input_file, "max_occupancy", args.count_all)
    save_analysis(customer_staff_ratio_results, args.input_file, "customer_staff_ratio", args.count_all)

    if (args.verbose):
        print(occupancy_time_results)
        print(max_occupancy_results)
    

if __name__ == "__main__":
    main()