"""Lambda function to manage WebSocket connections"""
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
CONNECTION_TABLE_NAME = os.environ['CONNECTION_TABLE_NAME']

def handler(event, context):
    # Log request
    LOGGER.info("Received message: %s", event)
    # Process incoming messages
    connection_id = event['requestContext']['connectionId']
    try:
        # Process $connect messages
        if event['requestContext']['routeKey'] == '$connect':
            connection_endpoint = 'https://' + event['requestContext']['domainName'] + '/' + event['requestContext']['stage']
            DYNAMODB_CLIENT.put_item(TableName=CONNECTION_TABLE_NAME, Item={
                'connectionId': {'S': connection_id},
                'connectionEndpoint': {'S': connection_endpoint}
                })
            LOGGER.info("Successfully added message to connections table")
            return {'statusCode': 200, 'body': 'Connected.'}
        # Process $disconnect messages
        elif event['requestContext']['routeKey'] == '$disconnect':
            DYNAMODB_CLIENT.delete_item(TableName=CONNECTION_TABLE_NAME, Key={'connectionId': {'S': connection_id}})
            LOGGER.info("Successfully deleted message from connections table")
            return {'statusCode': 200, 'body': 'Disconnected.'}
        # Process other messages
        else:
            LOGGER.info("Expected $connect or $disconnect.  Received: %s", event['requestContext']['routeKey'])
            return {'statusCode': 500, 'body': 'Failed to process message.'}
    except Exception:
        traceback.print_exc()
        return {'statusCode': 500, 'body': 'Failed to process message.'}
