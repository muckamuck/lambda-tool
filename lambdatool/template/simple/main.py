from utility import add_cors


@add_cors
def lambda_handler(event, context):
    '''
    This is the function that gets called when the lambda is invoked.
    Note: the name of the function is important for the deployment so only
    change it if you grok the consequences.

    Decorator:
        This contrived example will tell API Gateway to send out 42 as the
        answer. With the add_cors decorator it adds the needed CORS headers
        that will any application to call it. You can adjust the header as
        needed.

    Args:
        event - the dictionary filled with the bits of data from the invocation
        context - the context object of the invocation. For more information
        see http://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns:
        A dictionary that API Gateway understands. This just an example, your
        solution may return anything you may need.
    '''

    return {
        'statusCode': 200,
        'body': '42',
        'headers': {
            'Content-Type': 'text/plain'
        }
    }
