from functools import wraps


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
