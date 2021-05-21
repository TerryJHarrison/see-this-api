import boto3
import jwt
from botocore.exceptions import ClientError
from pprint import pprint

cognito = None


def res(code, body):
    return {
            "statusCode": code,
            'body': body,
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }


def lambda_handler(event, context):
    global cognito
    if not cognito:
        cognito = boto3.client('cognito-idp')

    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if not 'cognito:username' in decoded:
        return res(400, 'OwnerIDRequired')

    try:
        cognito.admin_delete_user(
            UserPoolId='us-east-1_sxLaqd27l',
            Username=decoded['cognito:username']
        )

        return res(200, "AccountClosed")
    except ClientError as e:
        pprint(e.response)
        return res(500, 'UnknownError')
