import boto3
import time
import json
import jwt
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


def put_collection(collection):
    global table
    collection['createdAt'] = int(time.time())
    collection['links'] = []
    item = collection

    response = table.put_item(
        Item=item,
        ConditionExpression="attribute_not_exists(id)"
    )
    return response


def does_collection_exist(collection_id):
    global table
    response = table.get_item(
        Key={
            'id': collection_id
        }
    )

    if 'Item' in response:
        return True
    else:
        return False


def lambda_handler(event, context):
    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if not 'cognito:username' in decoded:
        return res(400, 'OwnerIDRequired')
    username = decoded['cognito:username']

    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-link-collections')

    # Use provided path or generate one otherwise
    collection = json.loads(event['body'])
    collection['owner'] = username
    if does_collection_exist(collection['id']):
        return res(400, "CollectionAlreadyExists")

    try:
        put_collection(collection)
        return res(200, "CollectionCreated")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return res(400, "CollectionAlreadyExists")
        else:
            pprint(e.response)
            return res(500, 'UnknownError')


if __name__ == "__main__":
    test_response = lambda_handler({
        'headers': {
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiY29nbml0bzp1c2VybmFtZSI6InRqaGFycmlzb24iLCJpYXQiOjE1MTYyMzkwMjJ9.psL1JmW6CxOPcfjMKvWfYQ7TYTMZIocs9q0ctDxjTsA' # tjharrison
        },
        'body': json.dumps({
            'heading': 'Title Here',
            'id': 'saveTest',
            'links': [ {'redirectUrl': 'test.com', 'text': 'Description'},
                       {'redirectUrl': 'seeth.is', 'text': 'Description'}],
            'subheading': 'Short blurb here',
            'type': 'portfolio'
        })
    }, None)

    pprint(test_response, indent=2)