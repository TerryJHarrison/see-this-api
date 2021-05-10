import boto3

table = None


def not_found():
    return {
        'status': '200',
        'statusDescription': 'Link Not Found',
        'headers': {
            'location': [{
                'key': 'Location',
                'value': "/404.html"
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
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-short-links')

    response = table.get_item(Key={'link': link})
    if "Item" not in response:
        print(f"No URL found for link {link}")
        raise Exception('Not Found')
    return response['Item']['url']


def lambda_handler(event, context):
    request = event['Records'][0]['cf']['request']
    link = request["uri"].split("/")[2]

    if not link:
        print(f"No link found for request: {request}")
        return not_found()

    try:
        return redirect(find_url(link))
    except Exception as e:
        print(e)
        return not_found()