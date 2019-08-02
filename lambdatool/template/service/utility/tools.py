import sys
from functools import wraps
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from flask import Flask

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

from werkzeug.wrappers import BaseRequest


def add_cors(some_function):
    @wraps(some_function)
    def wrapper(*args, **kwargs):
        original_response = some_function(*args, **kwargs)
        if isinstance(original_response, dict):
            if 'headers' in original_response and isinstance(original_response['headers'], dict):
                original_response['headers']['Access-Control-Allow-Origin'] = '*'
            else:
                original_response['headers'] = {
                    'Access-Control-Allow-Origin': '*'
                }

        return original_response

    return wrapper


def make_environ(event):
    environ = {}

    for hdr_name, hdr_value in event['headers'].items():
        hdr_name = hdr_name.replace('-', '_').upper()
        if hdr_name in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
            environ[hdr_name] = hdr_value
            continue

        http_hdr_name = 'HTTP_{}'.format(hdr_name)
        environ[http_hdr_name] = hdr_value

    environ['REQUEST_METHOD'] = event['httpMethod']
    environ['PATH_INFO'] = event['path']
    environ['REMOTE_ADDR'] = event['requestContext']['identity']['sourceIp']
    environ['HOST'] = '%(HTTP_HOST)s:%(HTTP_X_FORWARDED_PORT)s' % environ
    environ['SCRIPT_NAME'] = ''
    environ['SERVER_PORT'] = environ['HTTP_X_FORWARDED_PORT']
    environ['SERVER_PROTOCOL'] = 'HTTP/1.1'
    environ['wsgi.url_scheme'] = environ['HTTP_X_FORWARDED_PROTO']
    environ['wsgi.input'] = StringIO(event['body'] or '')
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.multithread'] = False
    environ['wsgi.run_once'] = True
    environ['wsgi.multiprocess'] = False

    query_string = event['queryStringParameters']
    if query_string:
        environ['QUERY_STRING'] = urlencode(query_string)
    else:
        environ['QUERY_STRING'] = ''

    event_body = event['body']
    if event_body:
        environ['CONTENT_LENGTH'] = str(len(event_body))
    else:
        environ['CONTENT_LENGTH'] = ''

    BaseRequest(environ)

    return environ


class Response(object):
    def __init__(self):
        self.status = None
        self.response_headers = None

    def start_response(self, status, response_headers, exc_info=None):
        self.status = int(status[:3])
        self.response_headers = dict(response_headers)


class FlaskLambda(Flask):
    def __call__(self, event, context):
        if 'httpMethod' not in event:
            # In this "context" `event` is `environ` and
            # `context` is `start_response`, meaning the request didn't
            # occur via API Gateway and Lambda
            return super(FlaskLambda, self).__call__(event, context)

        response = Response()

        body = next(self.wsgi_app(
            make_environ(event),
            response.start_response
        )).decode('utf-8')

        return {
            'statusCode': response.status,
            'headers': response.response_headers,
            'body': body
        }
