import boto3
import time
import json
from botocore.exceptions import ClientError
from random_word import RandomWords
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


def put_link(link, redirect_url):
    global table
    item = {
        'link': link,
        'redirectUrl': redirect_url,
        'clickCount': 0,
        'createdAt': int(time.time()),
        'expiresAt': int(time.time()) + 604800 # 7 days
    }

    response = table.put_item(
        Item=item,
        ConditionExpression="attribute_not_exists(link)"
    )
    return response


def does_link_exist(link):
    global table
    response = table.get_item(
        Key={
            'link': link
        }
    )

    if 'Item' in response:
        pprint("Duplicate path generated")
        return True
    else:
        return False


def generate_random_path():
    global random
    if not random:
        random = RandomWords()

    verb = random.get_random_words(maxLength=5, includePartOfSpeech="verb", limit=1)[0]
    noun = random.get_random_words(maxLength=5, includePartOfSpeech="noun", limit=1)[0]
    path = f"{verb}-{noun}"
    # Recurse if necessary until a new link is generated
    return generate_random_path() if does_link_exist(path) else path


def lambda_handler(event, context):
    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-short-links')

    # Use provided path or generate one otherwise
    payload = json.loads(event['body'])
    path = generate_random_path() if not "link" in payload or payload['link'] == '' else payload["link"]

    try:
        put_link(path.lower(), payload["redirectUrl"])
        return res(200, json.dumps({'link': path}))
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return res(400, "LinkAlreadyExists")
        else:
            pprint(e.response)
            return res(500, 'UnknownError')


if __name__ == "__main__":
    test_response = lambda_handler({
        'body': json.dumps({
            'redirectUrl': 'https://test.com'
        })
    }, None)

    pprint(test_response, indent=2)