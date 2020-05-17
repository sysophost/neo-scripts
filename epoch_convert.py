# #!/usr/bin/python
import argparse
import csv
import sys
from datetime import datetime

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-ifile', '-i', type=str, default='file.csv', help='Path to input CSV')
PARSER.add_argument('-ofile', '-o', type=str, default='file_humandate.csv', help='Path to output CSV')
PARSER.add_argument('-col', '-c', type=int, action='append', required=True, help='Column with epoch time')
PARSER.add_argument('-delim', '-d', type=str, default=',', help='CSV delimiter')
PARSER.add_argument('-shortdate', '-s', action='store_true', help='Only output the date (no time value)')
PARSER.add_argument('-usdate', '-u', action='store_true', help='Output using US date format MM/DD/YY')
PARSER.add_argument('-dateformat', '-df', type=str, default='%H:%M:%S %d/%m/%Y', help='Custom format for date output (default %%H:%%M:%%S %%d/%%m/%%Y')

ARGS = PARSER.parse_args()

try:
    #read in data
    with open(ARGS.ifile, "r") as input_csv_file:
        CSV_READER = csv.reader(input_csv_file, delimiter=ARGS.delim)
        HEADERS = next(CSV_READER)
        LINES = list(CSV_READER)
    input_csv_file.close()

    #modify date and write updated data to a new file
    with open(ARGS.ofile, "w") as output_csv_file:
        CSV_WRITER = csv.writer(output_csv_file, delimiter=ARGS.delim)
        CSV_WRITER.writerow(HEADERS)

        if ARGS.shortdate and ARGS.usdate:
            date_format = '%m/%d/%Y'
        elif ARGS.usdate:
            date_format = '%H:%M:%S %m/%d/%Y'
        elif ARGS.shortdate:
            date_format = '%d/%m/%Y'
        else:
            date_format = ARGS.dateformat

        for row in LINES:
            if any(row):
                for col in ARGS.col:
                    epochtime = row[col]
                    row[col] = datetime.fromtimestamp(epochtime).strftime(date_format)

                CSV_WRITER.writerow(row)
        output_csv_file.close()

except (OSError, IOError):
    print(f"{ARGS.ifile} not found")
    sys.exit(1)
