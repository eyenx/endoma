from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from endoma.models import DockerHost
from endoma.views import HostController

class Command(BaseCommand):
    def handle(self, *args, **options):
        # update status if host is offline
        # this is done here to not have a scheduled job do it everytime
        # if status was longer than 15 minutes ago, update status
        # 15 minutes = 900 seconds
        for docker_host in DockerHost.objects.all():
            now=timezone.now()
            if (now - docker_host.last_update).seconds > 900:
                HostController().update_status(docker_host,'offline')
