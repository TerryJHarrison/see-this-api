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


def update_user_data(owner, user_data):
    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-user-data')

    update_expressions = []
    attribute_names = {}
    attribute_values = {}

    # Only update attributes that were passed in the update call
    if 'images' in user_data:
        update_expressions.append('#I = :i')
        attribute_names['#I'] = 'images'
        attribute_values[':i'] = user_data['images']

    if 'imgurApiKey' in user_data:
        update_expressions.append('#K = :k')
        attribute_names['#K'] = 'imgurApiKey'
        attribute_values[':k'] = user_data['imgurApiKey']

    if 'profileImage' in user_data:
        update_expressions.append('#P = :p')
        attribute_names['#P'] = 'profileImage'
        attribute_values[':p'] = user_data['profileImage']

    if 'profileImageSize' in user_data:
        update_expressions.append('#PS = :ps')
        attribute_names['#PS'] = 'profileImageSize'
        attribute_values[':ps'] = user_data['profileImageSize']

    if 'profileImageShape' in user_data:
        update_expressions.append('#PSH = :psh')
        attribute_names['#PSH'] = 'profileImageShape'
        attribute_values[':psh'] = user_data['profileImageShape']

    if 'qrCodeImage' in user_data:
        update_expressions.append('#Q = :q')
        attribute_names['#Q'] = 'qrCodeImage'
        attribute_values[':q'] = user_data['qrCodeImage']

    table.update_item(
        Key={'owner': owner},
        UpdateExpression=f"set {','.join(update_expressions)}",
        ExpressionAttributeNames=attribute_names,
        ExpressionAttributeValues=attribute_values
    )


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
    update_user_data(username, payload)
    return res(200, 'UserDataUpdated')


if __name__ == "__main__":
    test_response = lambda_handler({
        'headers': {
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiY29nbml0bzp1c2VybmFtZSI6InRqaGFycmlzb24iLCJpYXQiOjE1MTYyMzkwMjJ9.psL1JmW6CxOPcfjMKvWfYQ7TYTMZIocs9q0ctDxjTsA' # tjharrisonjr
        },
        'body': json.dumps({
            'images': [{'url': 'https://gardening.monster',
                        'text': 'Urban Gardening Blog'},
                       {'url': 'https://moderwoodworking.shop',
                        'text': 'Family owned and operated woodworking shop in North GA'}],
            'imgurApiKey': 'keyExample'
        })
    }, None)

    pprint(test_response, indent=2)
