import boto3
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


def get_link_collection(collection_id):
    global table

    response = table.get_item(Key={'id': collection_id})
    if "Item" not in response:
        pprint(f"No link collection found for id {collection_id}")
        raise Exception('Not Found')
    return response['Item']


def lambda_handler(event, context):
    payload = json.loads(event['body'])
    if not 'id' in payload:
        return res(400, 'CollectionIDRequired')

    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-link-collections')

    try:
        collection = get_link_collection(payload['id'])
        return res(200, collection)
    except Exception as e:
        if e.args[0] == "Not Found":
            return res(404, f'No collection found for id {payload["id"]}')
        else :
            return res(500, 'UnknownError')


if __name__ == "__main__":
    test_response = lambda_handler({
        'body': json.dumps({
            'id': 'test'
        })
    }, None)

    pprint(test_response, indent=2)
