import boto3
import logging
import io
import json
import jsonpickle
import os
import pydicom
import urllib.parse
from datetime import datetime, date, time, timezone


logger = logging.getLogger()
logger.setLevel(logging.INFO)

SSM_DDB_TABLE_NAME = '/lambda/orthanc/ddb/table_name'

s3_r = boto3.resource('s3')
ddb_r = boto3.resource('dynamodb')
ssm_c = boto3.client('ssm')

def read_dicom(bucket_name, key):
    logger.info(f"bucket_name = '{bucket_name}' key '{key}'")
    try:
        # Read S3 object into memory
        bucket = s3_r.Bucket(bucket_name)
        logger.info(f"bucket: {bucket}")
        object = bucket.Object(key)
        file_stream = io.BytesIO()
        # Could you just read the first 10k here?
        object.download_fileobj(file_stream)
        file_stream.seek(0)
        ds = pydicom.dcmread(file_stream, stop_before_pixels = True, defer_size = '2 KB')
        # print(ds)
        logger.info(f"Read a DICOM instance from {bucket_name}/{key} with SOP Instance UID {ds.SOPInstanceUID}")
    except pydicom.errors.InvalidDicomError as e:
        print(f"InvalidDicomError: {e}")
    except Exception as e:
        print(e)
    return(ds)

def ensure_ddb_table(table_name):
    try:
        table = ddb_r.Table(table_name)
        print(f"table {table_name} exists: {table}")
        table.load()
    except Exception as e:
        print(f"table {table_name} does not exist")
        try:            
            table = ddb_r.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 's3_object_key',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 's3_object_key',
                        'AttributeType': 'S'
                    },
                ],
                BillingMode='PAY_PER_REQUEST'
            )
        except Exception as e:
            print(e)
            raise(e)
    print(f"table: {table}")
    return(table)


def record_dcm_object(table, key, ds):
    logger.info(f"table {table}, key {key})")
    now = datetime.now(timezone.utc).isoformat()
    details = {
        's3_object_key': key,
        'metadata': ds.to_json()
    }
    print(f"details: {details}")
    try:
        response = table.put_item(
            Item = details
        )
        print(f"response: {response}")
    except Exception as e:
        print(e)
        raise(e)


def lambda_handler(event, context):
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info(f"type(event) = {type(event)}")
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    body = event['Records'][0]['body']
    jbody = json.loads(body)
    logger.info(f"body 1:\r" + json.dumps(jbody))
    record0 = jbody['Records'][0]
    s3 = record0['s3']
    logger.info(f"body 2 = {json.dumps(s3)}")

    response = ssm_c.get_parameter(Name = SSM_DDB_TABLE_NAME)
    table_name = response['Parameter']['Value']
    logger.info(f"table_name = {table_name}")

    bucket_name = s3['bucket']['name']
    key = urllib.parse.unquote_plus(s3['object']['key'], encoding='utf-8')
    ds = read_dicom(bucket_name, key)

    table = ensure_ddb_table(table_name)
    record_dcm_object(table, key, ds)
    
    message = {"hello": "world"}
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(message)
    }