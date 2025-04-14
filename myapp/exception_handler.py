from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import traceback

def custom_exception_handler(exc, context):
    # Спочатку викликаємо стандартний обробник
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Якщо помилка не оброблена DRF (наприклад, AttributeError)
    return Response({
        "error": str(exc),
        "type": type(exc).__name__,
        # "trace": traceback.format_exc(),  # опціонально, для дебагу
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)