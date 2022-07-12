# Max Occupancy Analysis

NCS NIVA Internal utility to generate a report showing the max number of people occupying an area and its first occuance time within defined periods given an **input time** and an **output time** 

## File Format

This utility expects an input file of a `.csv` format that contains the following headers 

#### Input File Format
||id|firstSeen|lastSeen|dwellTime|engagementTime|CrossLine
|-|-|-|-|-|-|-
|Data Type|`int`|`dateTime`|`dateTime`|`float`|`float`|`int`

### Output File Format
||timeStart|timeEnd|maxOccupants|firstOccuranceTime
|-|-|-|-|-
|Data Type|`dateTime`|`dateTime`|`int`|`dateTime`

## How to use

#### Install `requirements.txt`

`pip install requirements.txt`

### Commands

`python max_customers.py -i [input_file_path] -o [output_file_path] -g [granularity] [-a] [-v] `

- `-i, --input_file` - The input file path - **REQUIRED**
- `-o, --output_file`  - The output file path, defaults to `input_file_name`_output.csv -  *optional*
- `-g, --granularity` - The time window period in minutes, defaults to `60` minutes - *optional*
- `-a, --count_all` - Count all occupants, not just those who crossed the line - *optional*
- `-v, --verbose` - Verbosely list out the operations - *optional*

 
