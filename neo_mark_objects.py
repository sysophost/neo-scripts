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
PARSER.add_argument('-v', '-verbose', action='store_true', help='increase output verbosity')

ARGS = PARSER.parse_args()

if not ARGS.owned and not ARGS.highvalue:
    PARSER.error('-owned or -highvalue must be specified')

REQUEST_TIMEOUT = 30


def main():
    try:
        with open(ARGS.file) as objects_file:
            input_objects = objects_file.read().splitlines()
            print('Found {0} object(s) in {1}'.format(len(input_objects), ARGS.file))

    except (OSError, IOError):
        print('{0} not found'.format(ARGS.file))
        sys.exit(1)

    neo_url = 'http://{0}:{1}/db/data/transaction/commit'.format(ARGS.dbhost, ARGS.dbport)
    base64auth = base64.b64encode('{0}:{1}'.format(ARGS.username, ARGS.password))

    headers = {
        'Authorization': 'Basic {0}'.format(base64auth),
        'Content-Type': 'application/json'
    }

    find_query = construct_find_query(input_objects)
    find_response = query_neo(neo_url, headers, find_query)
    matched_objects = find_response.json()['results'][0]['data']
    matched_object_count = len(matched_objects)

    print('[i] Query returned {0} object(s)'.format(matched_object_count))
    if ARGS.verbose:
        for matched_object in matched_objects:
            print('{0}'.format(matched_object['row'][0]['name']))

    print('[i] Performing update of {0} records'.format(matched_object_count))

    update_query = construct_update_query(input_objects, ARGS.owned, ARGS.highvalue)
    update_response = query_neo(neo_url, headers, update_query)
    matched_objects = update_response.json()['results'][0]['data']
    if ARGS.verbose:
        for matched_object in matched_objects:
            print('{0}\r\n\tOwned:{1}\r\n\tHighvalue:{2}\r\n'.format(
                matched_object['row'][0]['name'], matched_object['row'][0]['owned'], matched_object['row'][0]['highvalue']))


def construct_find_query(matched_objects):
    data = {
        "statements": [{'statement': 'MATCH (n) WHERE n.name IN {0} RETURN n'.format(matched_objects)}]
    }
    return data


def construct_update_query(matched_objects, owned, highvalue):
    owned_action = 'n.owned=TRUE' if owned else ''
    highvalue_action = 'n.highvalue=TRUE' if highvalue else ''

    data = {
        "statements": [{'statement': 'MATCH (n) WHERE n.name IN {0} SET {1} {2} RETURN n'.format(matched_objects, owned_action, highvalue_action)}]
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


if __name__ == "__main__":
    main()
