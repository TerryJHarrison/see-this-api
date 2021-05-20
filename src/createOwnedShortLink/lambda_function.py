import boto3
import time
import jwt
import json
from botocore.exceptions import ClientError
from random_word import RandomWords

table = None
random = None


def put_link(link, redirect_url, owner):
    global table
    item = {
        'link': link,
        'redirectUrl': redirect_url,
        'clickCount': 0,
        'owner': owner,
        'createdAt': int(time.time()),
        'expiresAt': int(time.time()) + 1209600 # 14 days
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
        print("Duplicate path generated")
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

    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if not 'cognito:username' in decoded:
        return {
            "statusCode": 400,
            'body': 'OwnerIDRequired',
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }

    # Use provided path or generate one otherwise
    payload = json.loads(event['body'])
    path = generate_random_path() if not "link" in payload or payload['link'] == '' else payload["link"]

    try:
        put_link(path.lower(), payload["redirectUrl"], decoded['cognito:username'])
        return {
            'statusCode': 200,
            'body':  json.dumps({
                'link': path
            }),
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                "statusCode": 400,
                'body': "LinkAlreadyExists",
                'headers': {
                    'Access-Control-Allow-Origin': "*"
                }
            }
        else:
            print(e.response['Error']['Code'], e.response)
            return {
                'statusCode': 500,
                'body': 'UnknownError',
                'headers': {
                    'Access-Control-Allow-Origin': "*"
                }
            }
