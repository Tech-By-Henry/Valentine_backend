# leqtic_api/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env in local dev (Render will provide env vars in production)
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Basic
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY environment variable is required.")

DEBUG = os.getenv("DEBUG", "False") in ("True", "true", "1")

# Hosts
_allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
# If env var empty and DEBUG=True, allow localhost for quick dev
if _allowed_hosts:
    ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"] if DEBUG else []

# Project autodetection
PROJECT_MODULE = Path(__file__).resolve().parent.name
ROOT_URLCONF = f"{PROJECT_MODULE}.urls"
WSGI_APPLICATION = f"{PROJECT_MODULE}.wsgi.application"

# Apps
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",
    "rest_framework",

    # Local
    "valentines",
]

# Middleware (WhiteNoise before SecurityMiddleware to serve static files fast)
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -----------------------------
# Database (Postgres only)
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # fall back to explicit vars only if DATABASE_URL missing
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    if not POSTGRES_DB:
        raise ImproperlyConfigured(
            "Postgres config missing. Set DATABASE_URL or POSTGRES_DB and related POSTGRES_* env vars."
        )
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": POSTGRES_DB,
            "USER": os.getenv("POSTGRES_USER", ""),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", 600)),
            "OPTIONS": {"sslmode": os.getenv("POSTGRES_SSLMODE", "require")},
        }
    }
else:
    conn_max_age = int(os.getenv("POSTGRES_CONN_MAX_AGE", 600))
    # require SSL via dj-database-url and also allow explicit env override
    db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=conn_max_age, ssl_require=True)
    sslmode = os.getenv("POSTGRES_SSLMODE")
    if sslmode:
        db_config.setdefault("OPTIONS", {})["sslmode"] = sslmode
    DATABASES = {"default": db_config}

# -----------------------------
# Password validators
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------
# Internationalization / Static
# -----------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# WhiteNoise compressed manifest storage for production static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------
# REST FRAMEWORK
# -----------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

# -----------------------------
# CORS / CSRF
# -----------------------------
# Trusted origins (comma separated), e.g. https://your-frontend.com,https://your-backend.onrender.com
_csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [u.strip() for u in _csrf_origins.split(",") if u.strip()]
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False") in ("True", "true", "1")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "False") in ("True", "true", "1")

# -----------------------------
# Email (from env)
# -----------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587) or 587)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") in ("True", "true", "1")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# -----------------------------
# Production security flags (toggle with env)
# -----------------------------
# Force HTTPS in production (set to True in Render)
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") in ("True", "true", "1")

# Cookies
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True") in ("True", "true", "1")
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True") in ("True", "true", "1")

# HSTS
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", 3600))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True") in ("True", "true", "1")
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "False") in ("True", "true", "1")

# Misc
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
