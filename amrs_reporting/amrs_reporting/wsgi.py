"""
WSGI config for amrs_reporting project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, sys

path='/home/jdick/dev/amrs_reporting'

print path 
if path not in sys.path:
    sys.path.append(path)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
