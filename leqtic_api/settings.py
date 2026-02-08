import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root (where manage.py lives)
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Project auto-detection to avoid module name mismatches
PROJECT_MODULE = Path(__file__).resolve().parent.name
ROOT_URLCONF = f"{PROJECT_MODULE}.urls"
WSGI_APPLICATION = f"{PROJECT_MODULE}.wsgi.application"

# -----------------------
# SECURITY
# -----------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY environment variable is required.")

DEBUG = os.getenv("DEBUG", "False") in ("True", "true", "1")

_allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(",") if h.strip()]

# Useful when behind a reverse proxy / load balancer
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -----------------------
# APPS & MIDDLEWARE
# -----------------------
INSTALLED_APPS = [
    # Django core
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

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -----------------------
# TEMPLATES
# -----------------------
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

# -----------------------
# DATABASE (Postgres only — NO SQLITE FALLBACK)
# -----------------------
def _simple_parse_database_url(url: str):
    """
    Minimal parser for a postgres URL.
    Accepts postgres:// or postgresql://
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("postgres", "postgresql"):
        raise ImproperlyConfigured("DATABASE_URL must use postgres or postgresql scheme.")
    name = parsed.path.lstrip("/")
    if not name:
        raise ImproperlyConfigured("DATABASE_URL must include a database name.")
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": parsed.username or "",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or "5432"),
        "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", 600)),
        "OPTIONS": {"sslmode": os.getenv("POSTGRES_SSLMODE", "require")},
    }

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    try:
        import dj_database_url

        conn_max_age = int(os.getenv("POSTGRES_CONN_MAX_AGE", 600))
        # enforce SSL and parse the URL robustly
        db_config = dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=conn_max_age,
            ssl_require=True,  # ensure dj-database-url requests SSL
        )
        # allow explicit override via POSTGRES_SSLMODE env var
        sslmode = os.getenv("POSTGRES_SSLMODE")
        if sslmode:
            db_config.setdefault("OPTIONS", {})["sslmode"] = sslmode
        DATABASES = {"default": db_config}
    except Exception:
        # fallback parser (less robust, but will work for standard URLs)
        DATABASES = {"default": _simple_parse_database_url(DATABASE_URL)}
else:
    # Require explicit POSTGRES_* env vars if DATABASE_URL isn't present
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    if not POSTGRES_DB:
        raise ImproperlyConfigured(
            "Postgres configuration required. Set DATABASE_URL or POSTGRES_DB and related POSTGRES_* env vars."
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

# -----------------------
# AUTH VALIDATORS
# -----------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------
# I18N / TIME / STATIC
# -----------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------
# REST FRAMEWORK
# -----------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

# -----------------------
# CORS / CSRF
# -----------------------
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False") in ("True", "true", "1")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "False") in ("True", "true", "1")
_csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [u.strip() for u in _csrf_origins.split(",") if u.strip()]

# -----------------------
# EMAIL
# -----------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587) or 587)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") in ("True", "true", "1")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
