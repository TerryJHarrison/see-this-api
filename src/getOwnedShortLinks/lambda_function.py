import boto3
import jwt
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pprint import pprint

table = None
random = None


def get_owned_links(owner):
    global table
    response = table.query(
        IndexName="owner-link-index",
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression="link,redirectUrl,expiresAt,clickCount",
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
            if "clickCount" in link:
                link["clickCount"] = str(link["clickCount"])
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
        pprint(f"${e.response['Error']['Code']} ${e.response}`")
        return {
            'statusCode': 500,
            'body': 'UnknownError',
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }


if __name__ == "__main__":
    test_response = lambda_handler({
        'headers': {
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiY29nbml0bzp1c2VybmFtZSI6InRqaGFycmlzb24iLCJpYXQiOjE1MTYyMzkwMjJ9.psL1JmW6CxOPcfjMKvWfYQ7TYTMZIocs9q0ctDxjTsA' # tjharrisonjr
        }
    }, None)

    pprint(test_response, indent=2)