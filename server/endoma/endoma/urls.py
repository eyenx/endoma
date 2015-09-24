"""
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
# csrf_exempt for APIController
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.SimpleViewController.as_view(), name='index'),
    url(r'^login/$', views.LoginController.as_view(method='login'), name='login'),
    url(r'^logout/$', login_required(views.LoginController.as_view(method='logout')), name='logout'),
    url(r'^dashboard/$', login_required(views.SimpleViewController.as_view(template_name='dashboard.html')), name='dashboard'),
    url(r'^dashboard/host/$', login_required(views.HostController.as_view()), name='host'),
    url(r'^dashboard/host/(?P<host_id>[0-9]+)/$', login_required(views.HostController.as_view()), name='host'),
    url(r'^dashboard/container/$', login_required(views.ContainerController.as_view()), name='container'),
    url(r'^dashboard/container/(?P<container_id>[0-9]+)/$', login_required(views.ContainerController.as_view()), name='container'),
    url(r'^dashboard/task/$', login_required(views.TaskController.as_view()), name='task'),
    url(r'^dashboard/notification/$', login_required(views.NotificationController.as_view()), name='task'),
    url(r'^account/$', login_required(views.AccountController.as_view()), name='account'),
    url(r'^help/$', login_required(views.SimpleViewController.as_view(template_name='help.html')), name='help'),
    url(r'^api/$', csrf_exempt(views.ApiController.as_view()), name='api'),
    url(r'^api/poll/$', csrf_exempt(views.ApiController.as_view()), name='api'),
    url(r'^api/result/(?P<task_id>[0-9]+)/$', csrf_exempt(views.ApiController.as_view()), name='api'),
]
