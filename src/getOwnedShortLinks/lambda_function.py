import boto3
import jwt
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

table = None
random = None


def get_owned_links(owner):
    global table
    response = table.query(
        IndexName="owner-link-index",
        Select="ALL_ATTRIBUTES",
        KeyConditionExpression=Key('owner').eq(owner),
    )

    if 'Items' in response:
        return response['Items']
    else:
        return []


def lambda_handler(event, context):
    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-short-links')

    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if not 'cognito:username' in decoded:
        return {
            "statusCode": 400,
            'body': 'OwnerIDRequired',
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }

    try:
        links = get_owned_links(decoded["cognito:username"])
        for link in links:
            if "expiresAt" in link:
                link["expiresAt"] = str(link["expiresAt"])
        return {
            'statusCode': 200,
            'body': json.dumps({
                'links': links
            }),
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }
    except ClientError as e:
        print(e.response['Error']['Code'], e.response)
        return {
            'statusCode': 500,
            'body': 'UnknownError',
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }
