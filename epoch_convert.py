# #!/usr/bin/python
import time
import argparse
import csv
import sys

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-ifile', type=str, default='file.csv', help='Path to input CSV')
PARSER.add_argument('-ofile', type=str, default='file_humandate.csv', help='Path to output CSV')
PARSER.add_argument('-col', type=int, default=1, help='Column with epoch time')
PARSER.add_argument('-delim', type=str, default=',', help='CSV delimiter')
PARSER.add_argument('-shortdate', action='store_true', help='Only output the date (no time value)')
PARSER.add_argument('-usdate', action='store_true', help='Output using US date format MM/DD/YY')
PARSER.add_argument('-dateformat', type=str, default='%H:%M:%S %d/%m/%Y', help='Custom format for date output (default %%H:%%M:%%S %%d/%%m/%%Y')

ARGS = PARSER.parse_args()

try:
    #read in data
    LINES = ''
    with open(ARGS.ifile) as input_csv_file:
        CSV_READER = csv.reader(input_csv_file, delimiter=ARGS.delim)
        LINES = list(CSV_READER)
    input_csv_file.close()

    #modify date and write updated data to a new file
    with open(ARGS.ofile, "w") as output_csv_file:
        CSV_WRITER = csv.writer(output_csv_file, delimiter=ARGS.delim)
        LINE_COUNT = 0
        for row in LINES:
            epochtime = row[ARGS.col]
            if LINE_COUNT == 0:
                LINE_COUNT += 1
            else:
                date_format = ''

                if ARGS.shortdate:
                    date_format = '%d/%m/%Y'
                elif ARGS.usdate:
                    date_format = '%H:%M:%S %m/%d/%Y'
                elif ARGS.usdate and ARGS.shortdate:
                    date_format = '%m/%d/%Y'
                else:
                    date_format = ARGS.dateformat


                row[ARGS.col] = time.strftime(date_format, time.localtime(float(epochtime)))
            CSV_WRITER.writerow(row)
        output_csv_file.close()

except (OSError, IOError):
    print(f"{ARGS.ifile} not found")
    sys.exit(1)
