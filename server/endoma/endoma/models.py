from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DockerHost(models.Model):
    name=models.CharField(max_length=256)
    description=models.CharField(max_length=256)
    api_key=models.CharField(max_length=256)
    last_update=models.DateField(null=True)
    status=models.CharField(max_length=256,null=True)
    docker_version=models.CharField(max_length=256,null=True)
    user=models.ForeignKey(User)

class DockerContainer(models.Model):
    name=models.CharField(max_length=256)
    description=models.CharField(max_length=256)
    image=models.CharField(max_length=256)
    links=models.CharField(max_length=256,null=True)
    ports=models.CharField(max_length=256,null=True)
    last_update=models.DateField(null=True)
    status=models.CharField(max_length=256,null=True)
    docker_host=models.ForeignKey(DockerHost)

class HostStatusHistory(models.Model):
    timestamp=models.DateField()
    status_before=models.CharField(max_length=256)
    status_after=models.CharField(max_length=256)
    docker_host=models.ForeignKey(DockerHost)

class ContainerstatusHistory(models.Model):
    timestamp=models.DateField()
    status_before=models.CharField(max_length=256)
    status_after=models.CharField(max_length=256)
    docker_container=models.ForeignKey(DockerContainer)

class TaskTemplate(models.Model):
    name=models.CharField(max_length=256)
    description=models.CharField(max_length=256)
    command=models.CharField(max_length=256)

class Task(models.Model):
    timestamp=models.DateField()
#    status=models.CharField(max_length=256)
    task_template=models.ForeignKey(TaskTemplate)
    docker_container=models.ForeignKey(DockerContainer)
