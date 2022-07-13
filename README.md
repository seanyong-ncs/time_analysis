
  

# Occupancy Analysis 1.2

Occupancy Analysis is an NCS NIVA internal utility suite to generate reports based on **input time** and **output time**.

Currently generates 2 different reports

1. Max Occupancy Per Fixed Time Period
2. Occupancy Over Time

## Reports and Analyses

This utility expects an input file of a `.csv` format that contains the following headers

#### Input File Format

||id|firstSeen|lastSeen|dwellTime|engagementTime|CrossLine
|-|-|-|-|-|-|-
|Data Type|`int`|`dateTime`|`dateTime`|`float`|`float`|`int`

#### Output File Format

#### 1. `[filename]_max_occupancy.py`
||timeStart|timeEnd|maxOccupants|firstOccuranceTime
|-|-|-|-|-
|Data Type|`dateTime`|`dateTime`|`int`|`dateTime`

  
#### 2. `[filename]_occupancy_time.py`
||occupants|timeStart|timeEnd|duration [Seconds]
|-|-|-|-|-
|Data Type|`int`|`dateTime`|``dateTime``|`int`

  #### 3. `[filename]_max_occupancy.py`
||timeStart|timeEnd|customerStaffRatio
|-|-|-|-|-
|Data Type|`dateTime`|`dateTime`|`int`

## How to use

#### First Install `requirements.txt`

`pip install requirements.txt`

### Commands

`python main.py -i [input_file_path] -g [granularity] [-a] [-v] `

#### Example usage:
`python main.py -i data/ -g 60 `

#### Flags 
-  `-i, --input_path` - The input path. Can be a single folder/directory.  *Heatmaps will only generate if path is a directory of  `.csv` files* - **REQUIRED**

-  `-g, --granularity` - The time window period in minutes, defaults to `60` minutes - *optional*

-  `-a, --count_all` - Count all occupants, not just those who crossed the line - *optional*

-  `-v, --verbose` - Verbosely list out the operations - *optional*

## Heat Map
This utility can generate heatmaps from different days in a folder automatically

Example:

![Screenshot](assets\Max_Occupants_Per_Timeslot_example.png)


## Change Log

  `v1.2`
  - Added batch report generation feature
  - Added heatmap generation feature
  - Added customer-to-staff ratio report

`v1.1`

- Removed the output file flag option
- Added the "Occupancy Over Time" report
- Added a `_count_all` identifier to report names if `-a` flag is called