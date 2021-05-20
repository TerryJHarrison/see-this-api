import boto3
from pprint import pprint

table = None


not_found = {
    'status': '200',
    'statusDescription': 'Link Not Found',
    'headers': {
        'location': [{
            'key': 'Location',
            'value': "/"
        }]
    }
}


def redirect(url):
    return {
        'status': '302',
        'statusDescription': 'Found',
        'headers': {
            'location': [{
                'key': 'Location',
                'value': url
            }]
        }
    }


def find_url(link):
    global table

    response = table.get_item(Key={'link': link})
    if "Item" not in response:
        print(f"No URL found for link {link}")
        raise Exception('Not Found')
    return response['Item']['redirectUrl']


def increment_click_count(link):
    global table
    try:
        table.update_item(
            Key={'link': link},
            UpdateExpression='SET #C = #C + :i',
            ExpressionAttributeNames={"#C": "clickCount"},
            ExpressionAttributeValues={":i": 1}
        )
    except Exception as e:
        pprint('Increment click count error', e)
    finally:
        return True


def lambda_handler(event, context):
    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-short-links')

    request = event['Records'][0]['cf']['request']
    link = request["uri"].split("/")[2]

    if not link:
        print(f"No link found for request: {request}")
        return not_found

    increment_click_count(link)
    try:
        redirect_url = find_url(link)
        return redirect(redirect_url)
    except Exception as e:
        print(e)
        return not_found

if __name__ == "__main__":
    test_response = lambda_handler({
        'Records': [{
            'cf': {
                'request': {
                    'uri': '/l/example'
                }
            }}
        ]
    }, None)

    pprint(test_response, indent=2)