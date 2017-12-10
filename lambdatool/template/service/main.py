from utility import FlaskLambda
from flask import request
import json
import os

'''
The FlaskLambda object that is created is the entry point for the lambda. The
LambdaTool deployer expects this to be called 'lambda_handler'
'''
lambda_handler = FlaskLambda(__name__)


@lambda_handler.route('/', methods=['GET'])
def document():
    '''
    Redirect to the README doc

    Args:
        None

    Returns:
        tuple of (body, status code, content type) that API Gateway understands
    '''
    return (
        slash_html,
        200,
        {'Content-Type': 'text/html'}
    )


@lambda_handler.route('/answer', methods=['GET'])
def get_answer():
    '''
    Example of getting someething from function.properties

    Args:
        None

    Returns:
        tuple of (body, status code, content type) that API Gateway understands
    '''
    return (
        os.environ.get('ANSWER', '0'),
        200,
        {'Content-Type': 'text/html'}
    )


@lambda_handler.route('/food', methods=['GET', 'POST'])
def food():
    '''
    A contrived example function that will return some meta-data about the
    invocation.

    Args:
        None

    Returns:
        tuple of (body, status code, content type) that API Gateway understands
    '''
    data = {
        'form': request.form.copy(),
        'args': request.args.copy(),
        'json': request.json
    }
    return (
        json.dumps(data, indent=4, sort_keys=True),
        200,
        {'Content-Type': 'application/json'}
    )


if __name__ == '__main__':
    lambda_handler.run(debug=True)

slash_html = '''<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Lambtool Readme</title>
    <meta http-equiv="refresh" content="0;URL='https://github.com/muckamuck/lambda-tool/blob/master/README.md'" />
  </head>
  <body></body>
</html>
'''
