"""
File: init_tasktemplate.py
Comment: Custom administration command for initialize database with task templates
Project: EnDoMa
Author: Antonio Tauro
"""
# module imports
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from endoma.models import TaskTemplate
"""
Custom administration command for django
"""
class Command(BaseCommand):
    def handle(self, *args, **options):
        # load database with the five neede TaskTemplates
        # only do this if TaskTemplate table is empty
        if TaskTemplate.objects.count() == 0:
            tt1=TaskTemplate(name='delete',description='delete a container',command='remove_container(@@CONTAINERID@@)')
            tt1.save()
            tt2=TaskTemplate(name='stop',description='stop a container',command='stop(@@CONTAINERID@@)')
            tt2.save()
            tt3=TaskTemplate(name='start',description='start a container',command='start(@@CONTAINERID@@)')
            tt3.save()
            tt4=TaskTemplate(name='pull',description='pull an image',command='pull(@@IMAGE@@)')
            tt4.save()
            tt5=TaskTemplate(name='create',description='create a container',command='create_container(image=@@IMAGE@@,environment=@@ENVIRONMENT@@,ports=[@@PORT@@],host_config=docker.utils.create_host_config(@@HOST_CONFIG@@))')
            tt5.save()
