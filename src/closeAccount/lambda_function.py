import boto3
import jwt
from botocore.exceptions import ClientError

cognito = None


def lambda_handler(event, context):
    global cognito
    if not cognito:
        cognito = boto3.client('cognito-idp')

    decoded = jwt.decode(event['headers']['Authorization'], options={"verify_signature": False})
    if not 'cognito:username' in decoded:
        return {
            "statusCode": 400,
            'body': 'OwnerIDRequired',
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }

    try:
        cognito.admin_delete_user(
            UserPoolId='us-east-1_sxLaqd27l',
            Username=decoded['cognito:username']
        )

        return {
            'statusCode': 200,
            'body': "AccountClosed",
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }
    except ClientError as e:
        print(e.response['Error']['Code'], e.response)
        return {
            'statusCode': 500,
            'body': 'UnknownError',
            'headers': {
                'Access-Control-Allow-Origin': "*"
            }
        }
