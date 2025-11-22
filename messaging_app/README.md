# Messaging App with JWT Authentication

This Django REST Framework application implements a messaging system with JWT (JSON Web Tokens) and Session Authentication.

## Features

- JWT Authentication using `djangorestframework-simplejwt`
- Session Authentication support
- Custom permissions ensuring users can only access their own messages and conversations
- RESTful API endpoints for authentication

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

## Authentication Endpoints

### Obtain JWT Token
```bash
POST /api/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh JWT Token
```bash
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

### Verify JWT Token
```bash
POST /api/token/verify/
Content-Type: application/json

{
    "token": "your_access_token"
}
```

## Using JWT Tokens

Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Permissions

The app includes several custom permission classes:

- `CanAccessOwnData`: Ensures users can only access their own messages and conversations
- `IsMessageOwner`: Ensures users can only access messages they sent or received
- `IsConversationParticipant`: Ensures users can only access conversations they are part of
- `IsOwner`: Generic permission for objects with user/owner fields

## Configuration

JWT settings are configured in `messaging_app/settings.py`:

- Access token lifetime: 60 minutes
- Refresh token lifetime: 1 day
- Token rotation: Enabled
- Blacklist after rotation: Enabled

You can modify these settings in the `SIMPLE_JWT` dictionary in `settings.py`.

