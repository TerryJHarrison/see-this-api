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

def delete_collection(collection_id):
    global table
    response = table.delete_item(
        Key={'id': collection_id}
    )
    return response


def get_link_collection(collection_id):
    global table

    response = table.get_item(Key={'id': collection_id})
    if "Item" not in response:
        pprint(f"No link collection found for id {collection_id}")
        raise Exception('Not Found')
    return response['Item']


def lambda_handler(event, context):
    if not "headers" in event:
        return res(400, 'AuthorizationRequired')
    elif not "Authorization" in event['headers']:
        return res(400, 'AuthorizationRequired')

    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if not 'cognito:username' in decoded:
        return res(400, 'OwnerIDRequired')
    username = decoded['cognito:username']

    payload = json.loads(event['body'])
    if not 'id' in payload:
        return res(400, 'CollectionIDRequired')

    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-link-collections')

    try:
        collection = get_link_collection(payload['id'])
        if collection['owner'] != username:
            return res(403, 'Forbidden')
    except Exception as e:
        if e.args[0] == "Not Found":
            return res(404, f'No collection found for id {payload["id"]}')
        else :
            return res(500, 'UnknownError')

    delete_collection(payload['id'])

    return res(200, 'CollectionDeleted')


if __name__ == "__main__":
    test_response = lambda_handler({
        'headers': {
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiY29nbml0bzp1c2VybmFtZSI6InRqaGFycmlzb24iLCJpYXQiOjE1MTYyMzkwMjJ9.psL1JmW6CxOPcfjMKvWfYQ7TYTMZIocs9q0ctDxjTsA' # tjharrisonjr
        },
        'body': json.dumps({
            'id': 'saveTest'
        })
    }, None)

    pprint(test_response, indent=2)
