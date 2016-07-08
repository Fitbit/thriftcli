import json


def convert(request_body):
    """ Converts the JSON request body into an argument dictionary.

    :param request_body: The request body
    :type request_body: str
    :returns: The argument dictionary represented by the request body
    :rtype: dict

    """
    return json.loads(request_body)
