"""
RESE+ — Configuracoes Django
Versao com seguranca completa:
  - SECRET_KEY em .env
  - CORS restrito
  - JWT com autenticacao customizada via modelo Usuario
  - Permissoes IsAuthenticated nas views
"""
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import os

# ═══════════════════════════════════════════════════════════
#  CAMINHOS
# ═══════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ═══════════════════════════════════════════════════════════
#  SEGURANCA
# ═══════════════════════════════════════════════════════════
SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    raise Exception(
        'SECRET_KEY nao encontrada! Verifique o arquivo .env na raiz do projeto.'
    )

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    if host.strip()
]

# ═══════════════════════════════════════════════════════════
#  APPS INSTALADOS
# ═══════════════════════════════════════════════════════════
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'corsheaders',
    'dispositivos',
    
]

# ═══════════════════════════════════════════════════════════
#  MIDDLEWARE
# ═══════════════════════════════════════════════════════════
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ═══════════════════════════════════════════════════════════
#  CORS
# ═══════════════════════════════════════════════════════════
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:3000,http://localhost:8080'
    ).split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    print('')
    print('═══════════════════════════════════════════════════════')
    print('  RESE+ — Seguranca Ativa (JWT ATIVADO)')
    print('═══════════════════════════════════════════════════════')
    print(f'  DEBUG: {DEBUG}')
    print(f'  ALLOWED_HOSTS: {ALLOWED_HOSTS}')
    print(f'  CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}')
    print(f'  JWT Access: 1h | Refresh: 7 dias')
    print('═══════════════════════════════════════════════════════')
    print('')

# ═══════════════════════════════════════════════════════════
#  URLS E TEMPLATES
# ═══════════════════════════════════════════════════════════
ROOT_URLCONF = 'rese_plus_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ═══════════════════════════════════════════════════════════
#  BANCO DE DADOS
# ═══════════════════════════════════════════════════════════
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}

# ═══════════════════════════════════════════════════════════
#  INTERNACIONALIZACAO
# ═══════════════════════════════════════════════════════════
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Manaus'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ═══════════════════════════════════════════════════════════
#  REST FRAMEWORK — usa nossa autenticacao customizada
#  (UsuarioJWTAuthentication busca na tabela Usuario, nao no auth.User)
# ═══════════════════════════════════════════════════════════
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dispositivos.authentication.UsuarioJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DATETIME_FORMAT': '%d/%m/%Y %H:%M:%S',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ═══════════════════════════════════════════════════════════
#  SIMPLE JWT — rotacao desligada (refresh customizado em views.py)
# ═══════════════════════════════════════════════════════════
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ═══════════════════════════════════════════════════════════
#  HEADERS DE SEGURANCA HTTP (producao)
# ═══════════════════════════════════════════════════════════
if not DEBUG:
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ═══════════════════════════════════════════════════════════
#  SWAGGER — drf-spectacular
# ═══════════════════════════════════════════════════════════
SPECTACULAR_SETTINGS = {
    'TITLE': 'RESE+ API',
    'DESCRIPTION': 'Sistema de Rastreamento e Controle de Entrada e Saida de Equipamentos — Mineracao Taboca',
    'VERSION': '1.0.0',
    'CONTACT': {'name': 'Jaqueline Batista', 'email': 'rjaquelinesantos@gmail.com'},
    'LICENSE': {'name': 'Uso Restrito — Mineracao Taboca'},
    'SERVE_INCLUDE_SCHEMA': False,
}
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
