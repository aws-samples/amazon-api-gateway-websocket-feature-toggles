"""Lambda function to send a feature toggle update to connected clients"""
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
    LOGGER.info("Received event stream message %s", event)
    # Get active connections
    try:
        active_connections = DYNAMODB_CLIENT.scan(TableName=CONNECTION_TABLE_NAME, ProjectionExpression='connectionId,connectionEndpoint')
    except Exception:
        traceback.print_exc()
        return {'statusCode': 500, 'body': 'Failed to read active connections.'}
    # Iterate over changes in DynamoDB stream
    for record in event['Records']:
        # Iterate over active connections
        for connection in active_connections['Items']:
            try:
                # Isolate new feature toggle state
                if record['eventName'].upper() == 'REMOVE':
                    ddb_stream_capture = {'isRemoved': 'true', 'featureId': record['dynamodb']['Keys']}
                else:
                    ddb_stream_capture = record['dynamodb']['NewImage']
                # Send new feature toggle state to connection
                connection_endpoint = connection['connectionEndpoint']['S']
                connection_id = connection['connectionId']['S']
                api_gw_client = boto3.client('apigatewaymanagementapi', endpoint_url=connection_endpoint)
                api_gw_client.post_to_connection(ConnectionId=connection_id, Data=json.dumps(ddb_stream_capture))
                LOGGER.info("Posted update of %s to connection_id %s", record, connection_id)
            except api_gw_client.exceptions.GoneException:
                LOGGER.info("connection_id %s is no longer active.  Deleting this connection.", connection_id)
                DYNAMODB_CLIENT.delete_item(TableName=CONNECTION_TABLE_NAME, Key={'connectionId': {'S': connection_id}})
            except Exception:
                LOGGER.info("Failed to post message to connection %s", connection)
                traceback.print_exc()
    return {'statusCode': 200, 'body': 'Feature toggle update processed successfully.'}