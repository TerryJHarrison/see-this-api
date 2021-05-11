import boto3
import time
import botocore
from random_word import RandomWords

table = None
random = None


def put_link(link, url):
    global table
    # expires in 7 days
    response = table.put_item(
       Item={
            'link': link,
            'url': url,
            'expiresAt': int(time.time()) + 604800
        },
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
    return True if 'Item' in response else False


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
    path = event["link"] if "link" not in event or event["link"] is None else generate_random_path()

    try:
        put_link(path, event["url"])
        return {
            'statusCode': 200,
            'message': "Short link added",
            'link': path
        }
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                "statusCode": 400,
                "message": "LinkAlreadyExists"
            }
        else:
            print(e.response['Error']['Code'], e.response)
            return {
                'statusCode': 500,
                'message': 'UnknownError'
            }
