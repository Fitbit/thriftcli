import json


def validate(request_body):
    """ Validates that the request body is JSON format.

    :param request_body: The request body
    :type request_body: str
    :returns: True if the request body is valid JSON, False otherwise.
    :rtype: bool

    """
    try:
        json.loads(request_body)
    except ValueError:
        return False
    return True


def convert(request_body):
    """ Converts the JSON request body into an argument dictionary.

    :param request_body: The request body
    :type request_body: str
    :returns: The argument dictionary represented by the request body
    :rtype: dict

    """
    return json.loads(request_body)
