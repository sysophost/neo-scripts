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
                row[ARGS.col] = time.strftime('%H:%M:%S %d/%m/%Y', time.localtime(float(epochtime)))
            CSV_WRITER.writerow(row)
        output_csv_file.close()

except (OSError, IOError):
    print('{0} not found'.format(ARGS.file))
    sys.exit(1)
