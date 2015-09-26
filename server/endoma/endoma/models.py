from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DockerHost(models.Model):
    name=models.CharField(max_length=256)
    description=models.CharField(max_length=256,null=True)
    api_key=models.CharField(max_length=256)
    last_update=models.DateTimeField(auto_now=True,null=True)
    status=models.CharField(max_length=256)
    docker_version=models.CharField(max_length=256,null=True)
    to_delete=models.BooleanField(default=0)
    user=models.ForeignKey(User)

class DockerContainer(models.Model):
    name=models.CharField(max_length=256)
    description=models.CharField(max_length=256,null=True)
    image=models.CharField(max_length=256)
    links=models.CharField(max_length=256,null=True)
    ports=models.CharField(max_length=256,null=True)
    last_update=models.DateTimeField(auto_now=True,null=True)
    status=models.CharField(max_length=256)
    to_delete=models.BooleanField(default=0)
    docker_host=models.ForeignKey(DockerHost)

class HostStatusHistory(models.Model):
    timestamp=models.DateTimeField(auto_now_add=True)
    status_before=models.CharField(max_length=256)
    status_after=models.CharField(max_length=256)
    docker_host=models.ForeignKey(DockerHost)

class ContainerstatusHistory(models.Model):
    timestamp=models.DateTimeField(auto_now_add=True)
    status_before=models.CharField(max_length=256)
    status_after=models.CharField(max_length=256)
    docker_container=models.ForeignKey(DockerContainer)

class TaskTemplate(models.Model):
    name=models.CharField(max_length=256)
    description=models.CharField(max_length=256)
    command=models.CharField(max_length=256)

class Task(models.Model):
    create_timestamp=models.DateTimeField(auto_now_add=True)
    update_timestamp=models.DateTimeField(auto_now=True)
    status=models.CharField(max_length=256)
    task_template=models.ForeignKey(TaskTemplate)
    docker_container=models.ForeignKey(DockerContainer)
