import json

def make_return_response(data: dict) -> list:
    """
    Utility to wrap a dict as a standard JSON tool response.

    Args:
        data (dict): The data to return as JSON.

    Returns:
        list: A list with a single dict containing the JSON response.
    """
    return [
        {
            "type": "json",
            "content": json.dumps(data),
            "mimeType": "application/json"
        }
    ]