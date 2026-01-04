# In your app directory, create a file called middleware.py:
import logging
logger = logging.getLogger(__name__)

class PaymentDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log incoming requests to payment endpoints
        if 'payment' in request.path:
            logger.info(f"Payment request: {request.method} {request.path}")
            logger.info(f"POST data: {dict(request.POST)}")
            logger.info(f"GET params: {dict(request.GET)}")
        
        response = self.get_response(request)
        return response
    
# Create a file called middleware.py in your app
import traceback
from django.http import JsonResponse

class JsonExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        print(f"Exception in view: {exception}")
        print(traceback.format_exc())
        
        # If it's an AJAX request, return JSON error
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'message': str(exception)
            }, status=500)
        
        # Otherwise let Django handle it
        return None