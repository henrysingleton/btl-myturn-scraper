from scraper import build_output, get_session
import os

def lambda_handler(event, context):
    if event.get('queryStringParameters', {}).get('token', '') != os.environ.get('ACCESS_TOKEN', "NOT CONFIGURED"):
        return {
            'statusCode': 403,
            'body': "Unauthorized",
            'headers': { 'Content-Type': 'text/plain'},
        }

    session = get_session()
    output = build_output(session)
    return {
        'statusCode': 200,
        'body': "\r".join(output) if output else "Error",
        'headers': {
            'Content-Type': 'text/plain'
        },
    }

