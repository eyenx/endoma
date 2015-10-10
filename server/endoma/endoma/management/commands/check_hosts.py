from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from endoma.models import DockerHost,DockerContainer
from endoma.views import HostController,ContainerController

class Command(BaseCommand):
    def handle(self, *args, **options):
        # update status if host is offline
        # this is done here to not have a scheduled job do it everytime
        # if status was longer than 15 minutes ago, update status
        # 5 minutes = 300 seconds
        for docker_host in DockerHost.objects.filter(status='Online'):
            now=timezone.now()
            if (now - docker_host.last_update).seconds > 300:
                HostController().update_status(docker_host,'Offline')
                for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
                    ContainerController().update_status(docker_container,'Unknown')
