from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.views.generic import View
# import needed Http Classes
from django.http import HttpResponse,HttpRequest,HttpResponseRedirect
# import needed login decorators
from django.contrib.auth.decorators import login_required
# import my custom models
from .models import *
# random and string is used to generate random APIKey
import random
import string
# json module
import json
# time module for sleep
import time

# Viewcontrollers

class SimpleViewController(View):
    template_name='index.html'
    def get(self,request):
        return render(request,self.template_name)

class LoginController(View):
    template_name='login.html'
    method='login'
    def get(self,request):
        if self.method=='logout':
            logout(request)
            return HttpResponseRedirect('/login')
        else:
            return render(request,self.template_name)
    def post(self,request):
        user=authenticate(username=request.POST['username'],password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/dashboard')
        return render(request,self.template_name,{'error_message':'Login fehlgeschlagen'})

class HostController(View):
    template_name='host.html'
    def get(self,request,*args, **kwargs):
        # If host_id was given, return detail_host.html
        # example: dashboard/host/7/
        if 'host_id' in kwargs.keys():
            self.template_name='detail_host.html'
            docker_host=DockerHost.objects.get(id=kwargs['host_id'])
            return render(request,self.template_name,{'host_active':'active','dashboard_active':'active','docker_host':docker_host})
        # else return list of hosts
        # example: dashboard/host/
        docker_host_list=DockerHost.objects.filter(user=request.user)
        return render(request, self.template_name,{'docker_host_list':docker_host_list,'host_active':'active','dashboard_active':'active'})
#    else:
#        docker_host=DockerHost.objects.all()
#        return render(request, 'host_detail.html',{'docker_host':docker_host})
    def post(self,request,*args,**kwargs):
        docker_host=DockerHost(name=request.POST['hostname'],description=request.POST['hostdescription'],user=request.user,api_key="")
        # generate 128 character API Key
        for _ in range(32):
            docker_host.api_key+=random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits)
        docker_host.save()
        return HttpResponseRedirect('/dashboard/host')



class ContainerController(View):
    template_name='container.html'
    def get(self,request,*args,**kwargs):
        if 'container_id' in kwargs.keys():
            self.template_name='detail_container.html'
            docker_container=DockerContainer.objects.get(id=kwargs['container_id'])
            return render(request,self.template_name,{'container_active':'active','dashboard_active':'active','docker_container':docker_container})
        docker_host_list=DockerHost.objects.filter(user=request.user)
        docker_container_list=list()
        for docker_host in docker_host_list:
            for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
                docker_container_list.append(docker_container)
        return render(request,self.template_name,{'container_active':'active','dashboard_active':'active','docker_host_list':docker_host_list,'docker_container_list':docker_container_list})
    def post(self,request):
        docker_host=DockerHost.objects.get(id=request.POST['containerhost'])
        docker_container=DockerContainer(name=request.POST['containername'],description=request.POST['containerdescription'],image=request.POST['containerimage'],docker_host=docker_host)
        docker_container.save()
        return HttpResponseRedirect('/dashboard/container')
    def delete(self,request):
        return HttpResponse("test")

class TaskController(View):
    template_name='task.html'
    def get(self,request):
        return render(request,self.template_name,{'task_active':'active','dashboard_active':'active'})

class ApiController(View):
    def get(self,request):
        return HttpResponse('api')
    def post(self,request,*args,**kwargs):
        """
        possible paths
        /poll - Client -> Server - Client Polls and gives information about containers
        /result/<task_id> - Client -> Serve - Client gives Server result of Task # back

        possible datasets in json
        json dictionary of containers - Client -> Server - Client gives information about containers
        json dictionary with command to execute - Server -> Client - Server gives response to Client with information about what to execute
        json dictionary with result of command - Cleint -> Server - Client gives result of executed command
        """
        try:
            json_request=json.loads(request.body.decode('utf-8'))
            docker_host=self.check_api_key(json_request['api_key'])
        except(ValueError,KeyError):
            return HttpResponse("403")
        if docker_host and 'data' in json_request.keys():
            if request.path=='/api/poll/':
                # write data
                # self.update_containers(json_request['data'])
#                return HttpResponse(json_request['data'])
                task=self.get_next_task(docker_host)
                while not task:
                    time.sleep(5)
                    task=self.get_next_task(docker_host)
                return HttpResponse(json.dumps({'data':task.task_template.command.replace("@@IMAGE@@",task.docker_container.image)}))
            elif 'task_id' in kwargs.keys():
                return HttpResponse(json_request['data'])
            else:
                return HttpResponse("403")
        else:
            return HttpResponse("403")

    def check_api_key(self,api_key):
        docker_host=DockerHost.objects.filter(api_key=api_key)
        if docker_host:
            return docker_host
    def get_next_task(self,docker_host):
        for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
            try:
                return Task.objects.filter(docker_container=docker_container)[0]
            except(IndexError):
                return None





class NotificationController(View):
    template_name='notification.html'
    def get(self,request):
        return render(request,self.template_name,{'settings_active':'active'})

class AccountController(View):
    template_name='account.html'
    def get(self,request):
        return render(request, self.template_name,{'user':request.user,'account_active':'active'})
