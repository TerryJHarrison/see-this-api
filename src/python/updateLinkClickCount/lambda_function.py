import boto3
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


def update_link_click_count(collection, link_index):
    global table

    update_expressions = []
    attribute_names = {}
    attribute_values = {}

    # TODO: determine if concurrency safe
    link = collection['links'][int(link_index)]
    num_clicks = link['clickCount'] if 'clickCount' in link else 0
    collection['links'][int(link_index)]['clickCount'] = num_clicks + 1

    if 'links' in collection:
        update_expressions.append('#L = :l')
        attribute_names['#L'] = 'links'
        attribute_values[':l'] = collection['links']

    table.update_item(
        Key={'id': collection['id']},
        UpdateExpression="set #L = :l",
        ExpressionAttributeNames={'#L': 'links'},
        ExpressionAttributeValues={':l':  collection['links']}
    )


def get_link_collection(collection_id):
    global table

    response = table.get_item(Key={'id': collection_id})
    if "Item" not in response:
        pprint(f"No link collection found for id {collection_id}")
        raise Exception('Not Found')
    return response['Item']


def lambda_handler(event, context):
    if 'pathParameters' not in event:
        return res(400, "PathParametersRequired")
    elif 'id' not in event['pathParameters']:
        return res(400, "CollectionIDRequired")
    elif 'linkIndex' not in event['pathParameters']:
        return res(400, "LinkIndexRequired")

    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-link-collections')

    try:
        collection = get_link_collection(event['pathParameters']['id'])
        update_link_click_count(collection, event['pathParameters']['linkIndex'])
        return res(200, 'LinkClickCountUpdated')

    except Exception as e:
        if e.args[0] == "Not Found":
            return res(404, f"No collection found for id {event['pathParameters']['id']}")
        else:
            pprint(e)
            return res(500, 'UnknownError')


if __name__ == "__main__":
    test_response = lambda_handler({}, None)

    pprint(test_response, indent=2)