from datetime import timedelta

DEBUG = False

WTF_CSRF_ENABLED = False

MEMCACHED_URLS = ['127.0.0.1:11211']

PERMANENT_SESSION_LIFETIME = timedelta(days=3650)

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1

STATSD_HOST = '127.0.0.1'
STATSD_PORT = 8125

GRAPHITE_HOST = '127.0.0.1'
GRAPHITE_PORT = 2003

ASSETS_DEBUG = False
ASSETS_AUTO_BUILD = False
UGLIFYJS_EXTRA_ARGS = ['-c', '-m']

FLASK_ASSETS_USE_CDN = True
CDN_DOMAIN = 'd2rpyddsvhacm5.cloudfront.net'

BLACKLIST_EMAIL_DOMAINS = set([])

try:
    from local_settings import *
except ImportError:
    pass
