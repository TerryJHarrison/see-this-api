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


def update_link_collection(collection):
    global table

    update_expressions = []
    attribute_names = {}
    attribute_values = {}

    # Only update attributes that were passed in the update call
    if 'heading' in collection:
        update_expressions.append('#H = :h')
        attribute_names['#H'] = 'heading'
        attribute_values[':h'] = collection['heading']

    if 'headerAlign' in collection:
        update_expressions.append('#HA = :ha')
        attribute_names['#HA'] = 'headerAlign'
        attribute_values[':ha'] = collection['headerAlign']

    if 'headerTextColor' in collection:
        update_expressions.append('#HTC = :htc')
        attribute_names['#HTC'] = 'headerTextColor'
        attribute_values[':htc'] = collection['headerTextColor']

    if 'headerTextSize' in collection:
        update_expressions.append('#HTS = :hts')
        attribute_names['#HTS'] = 'headerTextSize'
        attribute_values[':hts'] = collection['headerTextSize']

    if 'subheading' in collection:
        update_expressions.append('#S = :s')
        attribute_names['#S'] = 'subheading'
        attribute_values[':s'] = collection['subheading']

    if 'subheaderAlign' in collection:
        update_expressions.append('#S = :s')
        attribute_names['#S'] = 'subheading'
        attribute_values[':s'] = collection['subheading']

    if 'subheaderTextColor' in collection:
        update_expressions.append('#S = :s')
        attribute_names['#S'] = 'subheading'
        attribute_values[':s'] = collection['subheading']

    if 'subheaderTextSize' in collection:
        update_expressions.append('#S = :s')
        attribute_names['#S'] = 'subheading'
        attribute_values[':s'] = collection['subheading']

    if 'links' in collection:
        update_expressions.append('#L = :l')
        attribute_names['#L'] = 'links'
        attribute_values[':l'] = collection['links']

    table.update_item(
        Key={'id': collection['id']},
        UpdateExpression=f"set {','.join(update_expressions)}",
        ExpressionAttributeNames=attribute_names,
        ExpressionAttributeValues=attribute_values
    )


def get_link_collection(collection_id):
    global table

    response = table.get_item(Key={'id': collection_id})
    if "Item" not in response:
        pprint(f"No link collection found for id {collection_id}")
        raise Exception('Not Found')
    return response['Item']


def lambda_handler(event, context):
    if "headers" not in event:
        return res(400, 'AuthorizationRequired')
    elif "Authorization" not in event['headers']:
        return res(400, 'AuthorizationRequired')

    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if 'cognito:username' not in decoded:
        return res(400, 'OwnerIDRequired')
    username = decoded['cognito:username']

    payload = json.loads(event['body'])
    if 'id' not in payload:
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
        else:
            pprint(e)
            return res(500, 'UnknownError')

    update_link_collection(payload)
    return res(200, 'CollectionUpdated')


if __name__ == "__main__":
    test_response = lambda_handler({
        'headers': {
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiY29nbml0bzp1c2VybmFtZSI6InRqaGFycmlzb24iLCJpYXQiOjE1MTYyMzkwMjJ9.psL1JmW6CxOPcfjMKvWfYQ7TYTMZIocs9q0ctDxjTsA' # tjharrisonjr
        },
        'body': json.dumps({
            'heading': 'Updated 2x',
            'id': 'test',
            'links': [{'redirectUrl': 'https://gardening.monster', 'text': 'Urban Gardening Blog'},
                    {'redirectUrl': 'https://moderwoodworking.shop', 'text': 'Family owned and operated woodworking shop in North GA'}],
            'subheading': 'Updated together'
        })
    }, None)

    pprint(test_response, indent=2)