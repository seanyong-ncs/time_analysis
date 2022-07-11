import argparse
from unittest import result
import pandas as pd
import numpy as np
from multiprocessing import Pool
from functools import partial

from py import process


def prepreocess_df(df):
    # Convert string to dateTime object
    df["firstSeen"] = pd.to_datetime(df["firstSeen"])
    df["lastSeen"] = pd.to_datetime(df["lastSeen"])

    # Sort by firstSeen
    df.sort_values(by="firstSeen", ascending=True, inplace=True)
    
    # Convert dateTime to timedelta
    initial_dt = df["firstSeen"].iloc[0]

    df["fs_timeStep"] = (df["firstSeen"] - initial_dt).dt.total_seconds().astype(int)
    df["ls_timeStep"] = (df["lastSeen"] - initial_dt).dt.total_seconds().astype(int)

    df = df.drop(columns=["firstSeen", "lastSeen", "dwellTime", "engagementTime", "crossLine"])
   
    return df

def generate_time_list_slice(df):
    max_time_step = df.loc[df["ls_timeStep"].idxmax()]["ls_timeStep"]
    results = np.zeros(max_time_step)

    for row in df.iterrows():
        rowList = np.zeros(max_time_step)
        # print(rowList)
        rowList[row[1][1]:row[1][2]] = 1
        results = rowList + results
    
    maxElement = np.amax(results)
    print(maxElement)
# 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="Input file path", required=True)
    parser.add_argument("-o", "--output_file", help="Output file path")
    parser.add_argument("-l", '--line_cross', action='store_true')
    args = parser.parse_args()

    raw_df = pd.read_csv(args.input_file)
    df = prepreocess_df(raw_df)

    # generate_time_list(df)
    generate_time_list_slice(df)
    # print(df.head())
    # print(df.dtypes)
    

if __name__ == "__main__":
    main()