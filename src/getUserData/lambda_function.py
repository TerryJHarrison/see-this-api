import boto3
import jwt
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pprint import pprint

table = None
random = None


def res(code, body):
    return {
        "statusCode": code,
        'body': body,
        'headers': {
            'Access-Control-Allow-Origin': "*"
        }
    }


def get_user_data(owner):
    global table
    response = table.query(
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression="images,imgurApiKey",
        KeyConditionExpression=Key('owner').eq(owner),
    )

    if 'Items' in response:
        return response['Items']
    else:
        return []


def lambda_handler(event, context):
    if "headers" not in event:
        return res(400, 'AuthorizationRequired')
    elif "Authorization" not in event['headers']:
        return res(400, 'AuthorizationRequired')

    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-user-data')

    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if 'cognito:username' not in decoded:
        return res(400, 'OwnerIDRequired')

    try:
        user_data = get_user_data(decoded["cognito:username"])
        return res(200, json.dumps({'user': user_data}))

    except ClientError as e:
        pprint(f"${e.response['Error']['Code']} ${e.response}`")
        return res(500, 'UnknownError')


if __name__ == "__main__":
    test_response = lambda_handler({
        'headers': {
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiY29nbml0bzp1c2VybmFtZSI6InRqaGFycmlzb24iLCJpYXQiOjE1MTYyMzkwMjJ9.psL1JmW6CxOPcfjMKvWfYQ7TYTMZIocs9q0ctDxjTsA' # tjharrisonjr
        }
    }, None)

    pprint(test_response, indent=2)
