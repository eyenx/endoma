"""
File: wsgi.py
Comment: Definition of wsgi for this application
         (left to default)
Project: EnDoMa
Author: Antonio Tauro
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "endoma.settings")

application = get_wsgi_application()
