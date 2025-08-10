from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            "success": False,
            "error": {
                "code": response.status_code,
                "message": response.data.get("detail", "An error occurred."),
                "details": response.data,
            },
        }
        response.data = custom_response

    return response
