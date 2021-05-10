import boto3
import time
import botocore

dynamodb = None


def put_link(link, url):
    global dynamodb
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('st-short-links')
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


def lambda_handler(event, context):
    try:
        put_link(event["link"], event["url"])
        return {
            'statusCode': 200,
            'message': "Short link added"
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
