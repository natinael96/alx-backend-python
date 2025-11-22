import logging
from datetime import datetime, timedelta
from collections import defaultdict
from django.http import HttpResponseForbidden, HttpResponse
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


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware that limits the number of chat messages a user can send
    within a certain time window, based on their IP address.
    Implements rate limiting: 5 messages per minute per IP address.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with rate limiting configuration.
        """
        self.get_response = get_response
        # Rate limiting configuration
        self.max_messages = 5  # Maximum messages allowed
        self.time_window = timedelta(minutes=1)  # Time window (1 minute)
        # Dictionary to track IP addresses and their request timestamps
        # Format: {ip_address: [timestamp1, timestamp2, ...]}
        self.ip_requests = defaultdict(list)
    
    def _get_client_ip(self, request):
        """
        Get the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _cleanup_old_requests(self, ip_address, current_time):
        """
        Remove request timestamps that are outside the time window.
        """
        cutoff_time = current_time - self.time_window
        self.ip_requests[ip_address] = [
            timestamp for timestamp in self.ip_requests[ip_address]
            if timestamp > cutoff_time
        ]
    
    def __call__(self, request):
        """
        Track POST requests to message endpoints and enforce rate limiting.
        """
        # Check if this is a POST request to message endpoints
        if request.method == 'POST' and (
            request.path.startswith('/api/messages/') or 
            request.path == '/api/messages/send/'
        ):
            # Get client IP address
            ip_address = self._get_client_ip(request)
            current_time = datetime.now()
            
            # Clean up old requests outside the time window
            self._cleanup_old_requests(ip_address, current_time)
            
            # Check if IP has exceeded the limit
            if len(self.ip_requests[ip_address]) >= self.max_messages:
                # Block the request and return error (429 Too Many Requests)
                return HttpResponse(
                    f"Rate limit exceeded. You can only send {self.max_messages} messages per {self.time_window.total_seconds()} seconds. "
                    f"Please try again later.",
                    status=429
                )
            
            # Add current request timestamp
            self.ip_requests[ip_address].append(current_time)
        
        # Process the request
        response = self.get_response(request)
        
        return response

