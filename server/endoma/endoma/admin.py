from django.contrib import admin

from .models import DockerHost,DockerContainer,ContainerstatusHistory,Task,TaskTemplate,HostStatusHistory

admin.site.register(DockerHost)
admin.site.register(DockerContainer)
admin.site.register(Task)
admin.site.register(TaskTemplate)
admin.site.register(ContainerstatusHistory)
admin.site.register(HostStatusHistory)
