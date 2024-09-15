from rest_framework.response import Response


def generate_response(success=True, message='success', status=200, custom_code=0, data=None, errors=None):
    resp_data = {
        "success": success,
        "message": message,
        "status": status,
        "custom_code": custom_code
    }
    if data is not None:
        resp_data["data"] = data
    if errors is not None:
        resp_data["errors"] = errors

    return Response(
        data=resp_data, status=status
    )
