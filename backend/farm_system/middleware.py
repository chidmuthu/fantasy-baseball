import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """Middleware to log all requests for debugging"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if settings.DEBUG:
            start_time = time.time()
            logger.debug(f"Request started: {request.method} {request.path}")
            logger.debug(f"Request user: {request.user}")
            logger.debug(f"Request data: {request.data if hasattr(request, 'data') else 'No data'}")
            logger.debug(f"Request GET params: {request.GET}")
            logger.debug(f"Request POST params: {request.POST}")
        
        response = self.get_response(request)
        
        if settings.DEBUG:
            duration = time.time() - start_time
            logger.debug(f"Request completed: {request.method} {request.path} - Status: {response.status_code} - Duration: {duration:.3f}s")
        
        return response 