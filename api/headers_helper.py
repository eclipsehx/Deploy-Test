"""Helper functions for generating custom headers."""

import os
import json
import base64


def generate_track_event_info_header():
    """
    Generate the Track-Event-Info header value.

    Returns:
        str: Base64 encoded JSON string of tracking info
    """
    plugin_name = os.getenv("PLUGIN_NAME", "ums-roo-code")
    plugin_version = os.getenv("PLUGIN_VERSION", "1.0.0")
    use_path = os.getenv("PLUGIN_USE_PATH", "ums-roo-代码库索引")
    function_code = os.getenv("PLUGIN_FUNCTION_CODE", "50")

    track_event_info = {
        "taskId": "default-embeddings-task-id",
        "pluginName": plugin_name,
        "pluginVersion": plugin_version,
        "usePath": use_path,
        "functionCode": function_code
    }

    json_str = json.dumps(track_event_info, ensure_ascii=False)
    base64_encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

    return base64_encoded


def get_custom_headers():
    """
    Get custom headers for API requests.

    Returns:
        dict: Dictionary of custom headers
    """
    plugin_name = os.getenv("PLUGIN_NAME")

    headers = {
        "X-App": plugin_name,
        # "Track-Event-Info": generate_track_event_info_header()
    }

    return headers
