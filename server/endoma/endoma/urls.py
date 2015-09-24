"""endoma URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
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
    url(r'^settings/$', login_required(views.SettingsController.as_view()), name='settings'),
    url(r'^account/$', login_required(views.AccountController.as_view()), name='account'),
    url(r'^help/$', login_required(views.SimpleViewController.as_view(template_name='help.html')), name='help'),
    url(r'^api/$', csrf_exempt(views.ApiController.as_view()), name='api'),
]
