import os
import json
import boto3

from utils import validate_slack_signature, parse_slack_payload, get_secret

SQS_QUEUE_NAME = os.environ['SQS_QUEUE_NAME']

secrets_manager = get_secret()
slack_signing_secret = secrets_manager['SLACK_SIGNING_SECRET']

sqs = boto3.resource('sqs')


def lambda_handler(event, context):
    print(event['headers'])
    print(event['body'])
    headers = event['headers']
    timestamp = headers['X-Slack-Request-Timestamp']
    request_body = event['body']
    slack_signature = headers['X-Slack-Signature']
    
    calculated_hash = validate_slack_signature(slack_signing_secret, request_body, timestamp)
    
    print("calculated_hash", calculated_hash)
    print("slack sigining signature", slack_signature)
    
    if calculated_hash != slack_signature:
        print("mismatched signatures!!!")
        return {
            'statusCode': 401,
            'body': "Unauthorized, invalid Slack signing secret"
        }
    
    print("matched signatures!!")

    payload = parse_slack_payload(request_body)
    print(payload)
    
    action = payload['actions'][0]
    instance_id = action['value']
    action_type = action['name']

    message_body = json.dumps({
        'instance_id': instance_id,
        'action': action_type
    })
    print(message_body)

    queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)
    queue.send_message(MessageBody=message_body)
    
    return {
        'statusCode': 200,
        'body': "*instance {action}d!*".format(action=action_type)
    }
