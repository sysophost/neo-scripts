# #!/usr/bin/python
import argparse
import base64
import sys

import requests

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-dbhost', type=str, default='127.0.0.1', help='IP address or hostname where Neo4J is running')
PARSER.add_argument('-dbport', type=str, default='7474', help='Neo4J listen port')
PARSER.add_argument('-username', type=str, default='neo4j', help='Neo4J username')
PARSER.add_argument('-password', type=str, default='Pa55w0rd', help='Neo4J password')
PARSER.add_argument('-file', type=str, default='file.txt', help='Path to file containing matched_object names')
PARSER.add_argument('-owned', action='store_true', help='Marked matched_objects as owned')
PARSER.add_argument('-highvalue', action='store_true', help='Marked matched_objects as high value')
PARSER.add_argument('-verbose', action='store_true', help='increase output verbosity')

ARGS = PARSER.parse_args()

if not ARGS.owned and not ARGS.highvalue:
    PARSER.error('-owned or -highvalue must be specified')

REQUEST_TIMEOUT = 30


verbose_print = print if ARGS.verbose else lambda *a, **k: None

def main():
    try:
        with open(ARGS.file) as objects_file:
            input_objects = objects_file.read().splitlines()
            print(f'Found {len(input_objects)} object(s) in {ARGS.file}')

    except (OSError, IOError):
        print(f'{ARGS.file} not found')
        sys.exit(1)

    neo_url = f'http://{ARGS.dbhost}:{ARGS.dbport}/db/data/transaction/commit'
    credString = f'{ARGS.username}:{ARGS.password}'
    base64auth = base64.b64encode(credString.encode()).decode('ascii')

    headers = {
        'Authorization': f'Basic {base64auth}',
        'Content-Type': 'application/json'
    }

    find_query = construct_find_query(input_objects)
    find_response = query_neo(neo_url, headers, find_query)
    matched_objects = find_response.json()['results'][0]['data']
    matched_object_count = len(matched_objects)

    print(f'[i] Query returned {matched_object_count} object(s)') 

    for matched_object in matched_objects:
            verbose_print(f"{matched_object['row'][0]['name']}")

    print(f'[i] Performing update of {matched_object_count} object(s)') 
    update_query = construct_update_query(input_objects, ARGS.owned, ARGS.highvalue)
    update_response = query_neo(neo_url, headers, update_query)
    matched_objects = update_response.json()['results'][0]['data']
    for matched_object in matched_objects:
        verbose_print(f"{matched_object['row'][0]['name']}\r\n\tOwned:{matched_object['row'][0]['owned']}\r\n\tHighvalue:{matched_object['row'][0]['highvalue']}\r\n")

def construct_find_query(matched_objects):
    data = {
        'statements': [{'statement': f'MATCH (n) WHERE n.name IN {matched_objects} RETURN n'}]
    }
    return data


def construct_update_query(matched_objects, owned, highvalue):
    owned_action = 'n.owned=TRUE' if owned else ''
    highvalue_action = 'n.highvalue=TRUE' if highvalue else ''
    delim = ', ' if owned and highvalue else ''

    data = {
        'statements': [{'statement': f'MATCH (n) WHERE n.name IN {matched_objects} SET {owned_action} {delim} {highvalue_action} RETURN n'}]
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
