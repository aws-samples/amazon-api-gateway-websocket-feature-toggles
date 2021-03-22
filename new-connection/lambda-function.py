"""Lambda function to send feature toggle status to new connections"""
import boto3
import os
import logging
import traceback
import json

# Initialize logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Initialize DDB client
DYNAMODB_CLIENT = boto3.client('dynamodb')

# Read table names from environment variable
FEATURE_TOGGLE_TABLE_NAME = os.environ['FEATURE_TOGGLE_TABLE_NAME']

def handler(event, context):
    # Log request
    LOGGER.info("Received event stream message %s", event)
    # Read current state of feature toggles
    try:
        active_feature_toggles = DYNAMODB_CLIENT.scan(TableName=FEATURE_TOGGLE_TABLE_NAME, ProjectionExpression='featureId,featureName,isActive')
    except Exception:
        traceback.print_exc()
        return {'statusCode': 500, 'body': 'Failed to read current state of feature toggles.'}
    # Capture inserts from DynamoDB stream
    for record in event['Records']:
        # Ignore connections that are not new
        if record['eventName'].upper() != 'INSERT':
            LOGGER.info("Ignoring non-insert message.")
        else:
            try:
                # Send current feature state to connection
                connection_endpoint = record['dynamodb']['NewImage']['connectionEndpoint']['S']
                connection_id = record['dynamodb']['NewImage']['connectionId']['S']
                api_gw_client = boto3.client('apigatewaymanagementapi', endpoint_url=connection_endpoint)
                api_gw_client.post_to_connection(ConnectionId=connection_id, Data=json.dumps(active_feature_toggles['Items']))
                LOGGER.info("Posted current state to connection_id %s", connection_id)
            except Exception:
                traceback.print_exc()
                LOGGER.info("Failed to post current state to record %s", record)
    return {'statusCode': 200, 'body': 'Updates processed.'}