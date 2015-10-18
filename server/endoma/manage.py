#!/usr/bin/env python
"""
File: manage.py
Comment: Manage script of django, needed to run the server
         (left to default)
Project: EnDoMa
Author: Antonio Tauro
"""
# module imports
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "endoma.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
