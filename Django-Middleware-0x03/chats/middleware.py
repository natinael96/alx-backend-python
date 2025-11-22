import logging
from datetime import datetime
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log each user's requests to a file.
    Logs timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware and set up logging.
        """
        self.get_response = get_response
        # Configure logger
        self.logger = logging.getLogger('request_logger')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if it doesn't exist
        if not self.logger.handlers:
            file_handler = logging.FileHandler('requests.log')
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
    
    def __call__(self, request):
        """
        Process the request and log user information.
        """
        # Get user information
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get user email or username
            user = getattr(request.user, 'email', None) or getattr(request.user, 'username', None) or str(request.user)
        else:
            user = 'Anonymous'
        
        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware that restricts access to the messaging app during certain hours.
    Denies access (403 Forbidden) if user accesses chat outside 6PM and 9PM.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response
        # Allowed hours: 6PM (18:00) to 9PM (21:00)
        self.allowed_start_hour = 18  # 6PM
        self.allowed_end_hour = 21    # 9PM
    
    def __call__(self, request):
        """
        Check the current server time and deny access if outside allowed hours.
        """
        # Check if the request is for chat-related endpoints
        if request.path.startswith('/api/conversations/') or request.path.startswith('/api/messages/'):
            # Get current server time
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # Check if current hour is outside the allowed range (6PM to 9PM)
            # Allowed: 18:00 to 20:59 (6PM to 8:59PM)
            # Denied: before 18:00 or after 20:59
            if current_hour < self.allowed_start_hour or current_hour >= self.allowed_end_hour:
                # Return 403 Forbidden
                return HttpResponseForbidden(
                    f"Access denied. Chat is only available between {self.allowed_start_hour}:00 (6PM) and {self.allowed_end_hour}:00 (9PM). "
                    f"Current time: {current_time.strftime('%H:%M:%S')}"
                )
        
        # Process the request if within allowed hours
        response = self.get_response(request)
        
        return response

