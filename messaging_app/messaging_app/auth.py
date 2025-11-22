"""
Custom authentication classes for the chats app.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication
from rest_framework.authentication import SessionAuthentication as BaseSessionAuthentication


class JWTAuthentication(BaseJWTAuthentication):
    """
    JWT Authentication class that extends the default JWT authentication.
    This allows for custom token validation if needed.
    """
    pass


class SessionAuthentication(BaseSessionAuthentication):
    """
    Session Authentication class for the chats app.
    This allows users to authenticate using Django sessions.
    """
    pass

