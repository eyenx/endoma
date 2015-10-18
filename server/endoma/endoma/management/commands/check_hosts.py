"""
File: check_hosts.py
Comment: Custom administration command for checking status of hosts
Project: EnDoMa
Author: Antonio Tauro
"""
# module imports
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from endoma.models import DockerHost,DockerContainer
from endoma.views import HostController,ContainerController

"""
Custom administration command of django
"""
class Command(BaseCommand):
    def handle(self, *args, **options):
        # update status if host is offline
        # this is done here to not have a scheduled job do it everytime
        # if status was longer than 5 minutes ago, update status
        # 5 minutes = 300 seconds
        for docker_host in DockerHost.objects.filter(status='Online'):
            # get time
            now=timezone.now()
            # if last update longer than 300 seconds ago
            if (now - docker_host.last_update).seconds > 300:
                # put host status to offline
                HostController().update_status(docker_host,'Offline')
                # put all his container to status "Unkown"
                for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
                    ContainerController().update_status(docker_container,'Unknown')
