import boto3
import json
from botocore.exceptions import ClientError
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



def get_all_links():
    global table
    response = table.scan(
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression="link,redirectUrl,clickCount,createdAt",
    )

    if 'Items' in response:
        return response['Items']
    else:
        return []


def calculate_link_stats(links):
    most_clicked_links = []
    highest_click_count = 0
    last_created_link = None
    last_created_at = 0

    pprint(links)
    for link in links:
        if link['clickCount'] > highest_click_count:
            most_clicked_links = [{'link': link['link'], 'redirectUrl': link['redirectUrl']}]
            highest_click_count = link['clickCount']
        elif link['clickCount'] == highest_click_count:
            most_clicked_links.append({'link': link['link'], 'redirectUrl': link['redirectUrl']})

        if 'createdAt' in link and link['createdAt'] > last_created_at:
            last_created_link = {'link': link['link'], 'redirectUrl': link['redirectUrl']}
            last_created_at = link['createdAt']

    return [most_clicked_links, last_created_link]

def lambda_handler(event, context):
    global table
    if not table:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('st-short-links')

    try:
        links = get_all_links()
        (most_clicked_links, last_created_link) = calculate_link_stats(links)

        return res(200, json.dumps({
            'MostClickedLinks': most_clicked_links,
            'LastCreatedShortLink': last_created_link
        }))
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return res(400, "LinkAlreadyExists")
        else:
            pprint(e.response)
            return res(500, 'UnknownError')


if __name__ == "__main__":
    test_response = lambda_handler({}, None)

    pprint(test_response, indent=2)