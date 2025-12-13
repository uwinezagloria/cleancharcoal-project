"""
Django settings for cleancharcoal_backend project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE SETTINGS FROM .ENV ---

# 1. SECURITY: Read SECRET_KEY from environment (CRITICAL)
# Use a default fallback only for development if needed, but production MUST use .env
SECRET_KEY = os.getenv(
    'SECRET_KEY', 
    'django-insecure-u(9+x9**dck%*m_hhd&5q(yh126ah*1wk6sam%a&ru)@l4829*' # Replace this with a long, unique value
) 

# 2. DEBUG: Read DEBUG from environment
# Convert env string ("True" or "False") to a Python boolean. Defaults to False.
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 3. HOSTS: Read ALLOWED_HOSTS from environment
# Use a safe fallback for development if DEBUG is True
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    # In production, ALLOWED_HOSTS must be a list of domain names!
    ALLOWED_HOSTS_STR = os.getenv("ALLOWED_HOSTS", "").replace(" ", "")
    ALLOWED_HOSTS = ALLOWED_HOSTS_STR.split(",") if ALLOWED_HOSTS_STR else []

# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cleancharcoal_app',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'djoser',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cleancharcoal_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cleancharcoal_backend.wsgi.application'

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# NOTE: For production, you should use os.getenv to configure PostgreSQL/MySQL

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC/MEDIA FILES ---
STATIC_URL = 'static/'
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# --- EMAIL CONFIGURATION ---

# Read the environment flag: USE_CONSOLE_EMAIL="True" or "False"
USE_CONSOLE_EMAIL = os.getenv("USE_CONSOLE_EMAIL", "True").lower() == "true"
IS_PRODUCTION = not USE_CONSOLE_EMAIL # Explicit variable for clarity

# Read the default sender email
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "CleanCharcoal <no-reply@cleancharcoal.local>"
)

if not IS_PRODUCTION:
    # ✅ DEVELOPMENT MODE — OTP prints in terminal
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    # ✅ PRODUCTION MODE — real email via SMTP
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    
    # Read credentials and add a timeout for robustness
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    EMAIL_TIMEOUT = 20 # New: Added a timeout (20 seconds) to prevent hanging
    
# --- REST FRAMEWORK & SPECTACULAR ---
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
SPECTACULAR_SETTINGS = {
    "TITLE": "CleanCharcoal API",
    "VERSION": "1.0.0",
    "SECURITY": [{"bearerAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }
    },
}
from datetime import timedelta

SIMPLE_JWT = {
    # Tokens will expire after 5 minutes of inactivity (Recommended for security)
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    
    # 🌟 CRITICAL CHANGE 🌟
    # This points to your custom serializer that enforces OTP verification and custom error messages.
    'TOKEN_OBTAIN_SERIALIZER': 'cleancharcoal_app.serializers.VerifiedTokenObtainPairSerializer',
}
DJOSER = {
    # 1. Email configuration: Use Djoser's default email sender classes
    'EMAIL': {
        'password_reset': 'djoser.email.PasswordResetEmail',
    },
    
    # 2. Frontend URL for the link: This is the URL where your frontend will handle the password reset form.
    # The uid and token parameters will be appended here.
    # Replace 'http://your-frontend.com' with the actual URL of your client application.
    'PASSWORD_RESET_CONFIRM_URL': 'http://your-frontend.com/reset-password/confirm/{uid}/{token}',
    
    'SERIALIZERS': {
       
    },
}
