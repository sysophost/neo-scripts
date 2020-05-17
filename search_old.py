# #!/usr/bin/python
import argparse
import base64
import csv
import sys
from datetime import datetime

import requests

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-dbhost', type=str, default='127.0.0.1', help='IP address or hostname where Neo4J is running')
PARSER.add_argument('-dbport', type=str, default='7474', help='Neo4J listen port')
PARSER.add_argument('-username', '-u', type=str, default='neo4j', help='Neo4J username')
PARSER.add_argument('-password', '-p', type=str, default='Pa55w0rd', help='Neo4J password')
PARSER.add_argument('-outfile', '-o', type=str, default='human_date_delta.csv', help='Path to output CSV')
PARSER.add_argument('-days', '-d', type=int, default=30, help='Number of days since last logon or password change (default 30)')
PARSER.add_argument('-filter', '-f', choices=['logon', 'password'], required=True, help='Search for password change')
PARSER.add_argument('-shortdate', '-s', action='store_true', help='Only output the date (no time)')
PARSER.add_argument('-usdate', '-us', action='store_true', help='Output using US date format MM/DD/YY')
PARSER.add_argument('-dateformat', '-df', type=str, default='%H:%M:%S %d/%m/%Y', help='Custom format for date output (default %%H:%%M:%%S %%d/%%m/%%Y')
PARSER.add_argument('-verbose', '-v', action='store_true', help='increase output verbosity')

ARGS = PARSER.parse_args()

REQUEST_TIMEOUT = 30

verbose_print = print if ARGS.verbose else lambda *a, **k: None

def main():
    neo_url = f'http://{ARGS.dbhost}:{ARGS.dbport}/db/data/transaction/commit'
    credString = f'{ARGS.username}:{ARGS.password}'
    base64auth = base64.b64encode(credString.encode()).decode('ascii')

    headers = {
        'Authorization': f'Basic {base64auth}',
        'Content-Type': 'application/json'
    }

    if ARGS.shortdate and ARGS.usdate:
        date_format = '%m/%d/%Y'
    elif ARGS.usdate:
        date_format = '%H:%M:%S %m/%d/%Y'
    elif ARGS.shortdate:
        date_format = '%d/%m/%Y'
    else:
        date_format = ARGS.dateformat

    if ARGS.filter == 'logon':
        field = 'lastlogontimestamp'
    else:
        field = 'pwdlastset'
    
    find_query = construct_find_query(field, ARGS.days)
    find_response = query_neo(neo_url, headers, find_query)
    matched_objects = find_response.json()['results'][0]['data']
    matched_object_count = len(matched_objects)

    print(f'[i] Query returned {matched_object_count} object(s)') 
    
    with open(ARGS.outfile, "w") as output_csv_file:
        CSV_WRITER = csv.writer(output_csv_file)
        CSV_WRITER.writerow(['Username',field,'Delta (Days)'])

        for matched_object in matched_objects:
            epochtime = matched_object['row'][0][field]
            human_time = datetime.fromtimestamp(epochtime).strftime(date_format)
            current_time = datetime.now().strftime(date_format)
            delta = (datetime.strptime(current_time, date_format) - datetime.strptime(human_time, date_format)).days
            name = matched_object['row'][0]['name']
            verbose_print(name)

            CSV_WRITER.writerow([name,human_time,delta])

    output_csv_file.close()
    print(f"[i] Output file written to {ARGS.outfile}")

def construct_find_query(field, days):#
    data = {
        'statements': [{'statement': f'MATCH (u:User) WHERE u.{field} <= (datetime().epochseconds - ({days} * 86400)) and NOT u.{field} IN [-1.0, 0.0] RETURN u ORDER BY u.name ASC'}]
    }
    return data

def query_neo(neo_url, headers, data):
    try:
        neo_response = requests.post(url=neo_url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
        neo_response.raise_for_status()
        return neo_response
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)


if __name__ == '__main__':
    main()
