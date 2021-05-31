import boto3
import jwt
import json
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


def update_link(link, redirect_url):
    global table

    table.update_item(
        Key={'link': link},
        UpdateExpression='SET #U = :u',
        ExpressionAttributeNames={"#U": "redirectUrl"},
        ExpressionAttributeValues={":u": redirect_url}
    )


def get_link(link):
    global table

    response = table.get_item(Key={'link': link})
    if "Item" not in response:
        pprint(f"No URL found for link {link}")
        raise Exception('Not Found')
    return response['Item']


def lambda_handler(event, context):
    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if not 'cognito:username' in decoded:
        return res(400, 'OwnerIDRequired')
    username = decoded['cognito:username']

    payload = json.loads(event['body'])
    if not 'link' in payload:
        return res(400, 'LinkRequired')
    if not 'redirectUrl' in payload:
        return res(400, 'RedirectURLRequired')

    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-short-links')

    try:
        short_link = get_link(payload['link'])
        if short_link['owner'] != username:
            return res(403, 'Forbidden')
    except Exception as e:
        if e.args[0] == "Not Found":
            return res(404, f'No link found for {payload["link"]}')
        else:
            pprint(e)
            return res(500, 'UnknownError')

    update_link(payload['link'], payload['redirectUrl'])
    return res(200, 'LinkUpdated')


if __name__ == "__main__":
    test_response = lambda_handler({
        'headers': {
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiY29nbml0bzp1c2VybmFtZSI6InRqaGFycmlzb24iLCJpYXQiOjE1MTYyMzkwMjJ9.psL1JmW6CxOPcfjMKvWfYQ7TYTMZIocs9q0ctDxjTsA' # tjharrisonjr
        },
        'body': json.dumps({
            'link': 'integration-test',
            'redirectUrl': 'https://update.com'
        })
    }, None)

    pprint(test_response, indent=2)