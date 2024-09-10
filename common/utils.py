from rest_framework.response import Response


def generate_response(success=True, message='success', status=200, custom_code=0, data=None):
    resp_data = {
        "success": success,
        "message": message,
        "status": status,
        "custom_code": custom_code
    }
    if data:
        resp_data["data"] = data
    return Response(
        data=resp_data, status=status
    )
