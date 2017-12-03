from utility import add_cors


@add_cors
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': '42',
        'headers': {
            'Content-Type': 'text/plain'
        }
    }
