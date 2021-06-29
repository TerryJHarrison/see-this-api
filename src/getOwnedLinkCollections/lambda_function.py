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


def get_owned_link_collections(owner):
    global table
    response = table.query(
        IndexName="owner-id-index",
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression="id,heading,collectionType",
        KeyConditionExpression=Key('owner').eq(owner),
    )

    if 'Items' in response:
        return response['Items']
    else:
        return []


def lambda_handler(event, context):
    if not "headers" in event:
        return res(400, 'AuthorizationRequired')
    elif not "Authorization" in event['headers']:
        return res(400, 'AuthorizationRequired')

    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-link-collections')

    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if not 'cognito:username' in decoded:
        return res(400, 'OwnerIDRequired')

    try:
        collections = get_owned_link_collections(decoded["cognito:username"])
        return res(200, json.dumps({'collections': collections}))

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