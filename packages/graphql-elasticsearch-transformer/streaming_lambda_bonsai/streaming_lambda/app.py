import base64
import datetime
import json
import logging
import os
import time
import traceback
import requests
from urllib.parse import urlparse, quote
from boto3.dynamodb.types import TypeDeserializer

# The following BONSAI parameters are required replicate 
# DynamoDB items to a single Bonsai cluster.  
BONSAI_ENDPOINT = os.environ['BONSAI_ENDPOINT']
BONSAI_ACCESS_KEY = os.environ['BONSAI_ACCESS_KEY']
BONSAI_ACCESS_SECRET = os.environ['BONSAI_ACCESS_SECRET']
DEBUG = True if os.environ['DEBUG'] == "1" else False

# The lambda posts a single string of one or more JSON rows 
# to the ElasticSearch _bulk API path.

# ElasticSearch 6 deprecated having multiple mapping types in an index. Default to doc.
DOC_TYPE = 'doc'
ES_MAX_RETRIES = 3              # Max number of retries for exponential backoff

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
logger.info("Streaming to ElasticSearch")

# custom encoder changes
# - sets to lists
class DDBTypesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

# Subclass of boto's TypeDeserializer for DynamoDB to adjust for DynamoDB Stream format.
class StreamTypeDeserializer(TypeDeserializer):
    def _deserialize_n(self, value):
        return float(value)

    def _deserialize_b(self, value):
        return value  # Already in Base64


class ES_Exception(Exception):
    '''Capture status_code from request'''
    status_code = 0
    payload = ''

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        Exception.__init__(
            self, 'ES_Exception: status_code={}, payload={}'.format(status_code, payload))

# Low-level POST data to Amazon Elasticsearch Service generating a Sigv4 signed request
def post_data_to_es(payload, user, password, host, path, method='POST', proto='https://'):
    logger.debug('The payload is %s', payload)
    logger.debug('The host is %s', host)
    logger.debug('The proto is %s', proto)
    logger.debug('The method is %s', method)
    logger.debug('The path is %s', path)
    headers = {'Content-type': 'application/json'}
    url = proto + host + path
    r = requests.post(url, headers=headers, auth=(user, password), verify=True, data=payload)
    logger.debug('Status code %d', r.status_code)
    logger.debug('Response text is %s', r.text)
    return r.text

# High-level POST data to Amazon Elasticsearch Service with exponential backoff
# according to suggested algorithm: http://docs.aws.amazon.com/general/latest/gr/api-retries.html
def post_to_es(payload):
    '''Post data to ES cluster with exponential backoff'''

    es_url = urlparse(BONSAI_ENDPOINT)
    # Extract the domain name in BONSAI_ENDPOINT
    es_endpoint = es_url.netloc or es_url.path

    # Post data with exponential backoff
    retries = 0
    while retries < ES_MAX_RETRIES:
        if retries > 0:
            seconds = (2 ** retries) * .1
            logger.debug('Waiting for %.1f seconds', seconds)
            time.sleep(seconds)

        try:
            es_ret_str = post_data_to_es(
                payload, BONSAI_ACCESS_KEY, BONSAI_ACCESS_SECRET, es_endpoint, '/_bulk')
            logger.debug('Return from ES: %s', es_ret_str)
            es_ret = json.loads(es_ret_str)

            if es_ret['errors']:
                logger.error(
                    'ES post unsuccessful, errors present')
                # Filter errors
                es_errors = [item for item in es_ret['items']
                            if item.get('index').get('error')]
                logger.error('List of items with errors: %s',
                            json.dumps(es_errors))
            else:
                logger.info('ES post successful')
            break  # Sending to ES was ok, break retry loop
        except ES_Exception as e:
            if (e.status_code >= 500) and (e.status_code <= 599):
                retries += 1  # Candidate for retry
            else:
                raise  # Stop retrying, re-raise exception


# Extracts the DynamoDB table from an ARN
# ex: arn:aws:dynamodb:eu-west-1:123456789012:table/table-name/stream/2015-11-13T09:23:17.104 should return 'table-name'
def get_table_name_from_arn(arn):
    return arn.split(':')[5].split('/')[1]


# Compute a compound doc index from the key(s) of the object in lexicographic order: "k1=key_val1|k2=key_val2"
def compute_doc_index(keys_raw, deserializer, formatIndex=False):
    index = []
    for key in sorted(keys_raw):
        if formatIndex:
            index.append('{}={}'.format(
                key, deserializer.deserialize(keys_raw[key])))
        else:
            index.append(deserializer.deserialize(keys_raw[key]))
    return '|'.join(index)


def _lambda_handler(event, context):
    logger.debug('Event: %s', event)
    records = event['Records']
    now = datetime.datetime.utcnow()

    ddb_deserializer = StreamTypeDeserializer()
    es_actions = []  # Items to be added/updated/removed from ES - for bulk API
    cnt_insert = cnt_modify = cnt_remove = 0

    for record in records:
        # Handle both native DynamoDB Streams or Streams data from Kinesis (for manual replay)
        logger.debug('Record: %s', record)
        if record.get('eventSource') == 'aws:dynamodb':
            ddb = record['dynamodb']
            ddb_table_name = get_table_name_from_arn(record['eventSourceARN'])
            doc_seq = ddb['SequenceNumber']
        elif record.get('eventSource') == 'aws:kinesis':
            ddb = json.loads(base64.b64decode(record['kinesis']['data']))
            ddb_table_name = ddb['SourceTable']
            doc_seq = record['kinesis']['sequenceNumber']
        else:
            logger.error('Ignoring non-DynamoDB event sources: %s',
                        record.get('eventSource'))
            continue

        # Compute DynamoDB table, type and index for item
        doc_table = ddb_table_name.lower()
        doc_type = DOC_TYPE
        doc_table_parts = doc_table.split('-')
        doc_es_index_name = doc_table_parts[0] if len(doc_table_parts) > 0  else doc_table

        # Dispatch according to event TYPE
        event_name = record['eventName'].upper()  # INSERT, MODIFY, REMOVE
        logger.debug('doc_table=%s, event_name=%s, seq=%s',
                    doc_table, event_name, doc_seq)

        # Treat events from a Kinesis stream as INSERTs
        if event_name == 'AWS:KINESIS:RECORD':
            event_name = 'INSERT'

        # Update counters
        if event_name == 'INSERT':
            cnt_insert += 1
        elif event_name == 'MODIFY':
            cnt_modify += 1
        elif event_name == 'REMOVE':
            cnt_remove += 1
        else:
            logger.warning('Unsupported event_name: %s', event_name)

        is_ddb_insert_or_update = (event_name == 'INSERT') or (event_name == 'MODIFY')
        is_ddb_delete = event_name == 'REMOVE'
        image_name = 'NewImage' if is_ddb_insert_or_update else 'OldImage'

        if image_name not in ddb:
            logger.warning(
                'Cannot process stream if it does not contain ' + image_name)
            continue
        logger.debug(image_name + ': %s', ddb[image_name])
        # Deserialize DynamoDB type to Python types
        doc_fields = ddb_deserializer.deserialize({'M': ddb[image_name]})

        logger.debug('Deserialized doc_fields: %s', doc_fields)

        if ('Keys' in ddb):
            doc_id = compute_doc_index(ddb['Keys'], ddb_deserializer)
        else:
            logger.error('Cannot find keys in ddb record')

        # Generate JSON payload
        doc_json = json.dumps(doc_fields, cls=DDBTypesEncoder)

        # If DynamoDB INSERT or MODIFY, send 'index' to ES
        if is_ddb_insert_or_update:
            # Generate ES payload for item
            action = {'index': {'_index': doc_es_index_name,
                                '_type': doc_type, '_id': doc_id}}
            # Action line with 'index' directive
            es_actions.append(json.dumps(action))
            # Payload line
            es_actions.append(doc_json)
            # migration step remove old key if it exists
            if ('id' in doc_fields) and (event_name == 'MODIFY') :
                action = {'delete': {'_index': doc_es_index_name, '_type': doc_type,
                    '_id': compute_doc_index(ddb['Keys'], ddb_deserializer, True)}}
                es_actions.append(json.dumps(action))
        # If DynamoDB REMOVE, send 'delete' to ES
        elif is_ddb_delete:
            action = {'delete': {'_index': doc_es_index_name,
                                '_type': doc_type, '_id': doc_id}}
            # Action line with 'index' directive
            es_actions.append(json.dumps(action))

    # Prepare bulk payload
    es_actions.append('')  # Add one empty line to force final \n
    es_payload = '\n'.join(es_actions)
    logger.info('Posting to ES: inserts=%s updates=%s deletes=%s, total_lines=%s, bytes_total=%s',
                cnt_insert, cnt_modify, cnt_remove, len(es_actions) - 1, len(es_payload))
    post_to_es(es_payload)  # Post to ES with exponential backoff


# Global lambda handler - catches all exceptions to avoid dead letter in the DynamoDB Stream
def lambda_handler(event, context):
    try:
        return _lambda_handler(event, context)
    except Exception:
        logger.error(traceback.format_exc())
