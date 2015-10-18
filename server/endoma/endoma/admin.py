"""
File: admin.py
Comment: definition of admin application (not needed in production)
Project: EnDoMa
Author: Antonio Tauro
"""
# module imports
from django.contrib import admin
# import models
from .models import DockerHost,DockerContainer,ContainerstatusHistory,Task,TaskTemplate,HostStatusHistory

admin.site.register(DockerHost)
admin.site.register(DockerContainer)
admin.site.register(Task)
admin.site.register(TaskTemplate)
admin.site.register(ContainerstatusHistory)
admin.site.register(HostStatusHistory)
