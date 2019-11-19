import os
import json
import hmac
import hashlib
import urllib.parse

import boto3
import base64
from botocore.exceptions import ClientError


def validate_slack_signature(signing_secret, req_body, timestamp):
    signing_secret = str.encode(signing_secret)
    sig_basestring = str.encode('v0:' + timestamp + ':' + req_body)  # creating text to hash

    digest = hmac.new(signing_secret, msg=sig_basestring, digestmod=hashlib.sha256).hexdigest()
    return "v0=" + digest


def parse_slack_payload(req_body):
    if req_body.startswith("payload="):
        req_body = req_body.replace("payload=", "")

    decoded_payload = urllib.parse.unquote(req_body)
    url_params = json.loads(decoded_payload)
    return url_params
    
    
def get_secret():
    # secret_name = "ec2-instance-bot-secret"
    secret_name = os.environ['SECRET_NAME']
    region_name = os.environ['REGION_NAME']

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(e)
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.

        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(decoded_binary_secret)
