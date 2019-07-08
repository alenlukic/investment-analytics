def build_response_context(response):
    """ Builds a dictionary containing useful API response data when a non-200 status code is received.

    Parameters:
        response (requests.Response): response JSON
    """

    return {
        'Status': response.status_code,
        'Reason': response.reason,
        'Content': response.content,
        'Headers': response.headers,
        'Url': response.url
    }
