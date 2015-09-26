from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.views.generic import View
# import needed HTTP Classes from django framework
from django.http import HttpResponse,HttpRequest,HttpResponseRedirect
# import needed login decorators from django framework
from django.contrib.auth.decorators import login_required
# django utils timezone to genarate datetime objects
from django.utils import timezone
# import my custom models
from .models import *
# random and string is used to generate random APIKey
import random
import string
# json module for API communication
import json
# time module for sleep (used in the APIController)
import time

# Viewcontrollers

"""
SimpleViewController
needed for simple views
URLs:
    /
"""
class SimpleViewController(View):
    # Default template
    template_name='index.html'
    # HTTP GET
    def get(self,request):
        # render template
        return render(request,self.template_name)
"""
LoginController
needed for login and logout
URLs:
    /login
    /logout
"""
class LoginController(View):
    # Default template
    template_name='login.html'
    # set method, login or logout. Default: login
    method='login'
    # HTTP GET
    def get(self,request):
        # if logout method
        if self.method=='logout':
            logout(request)
            return HttpResponseRedirect('/login')
        # if login method show login view
        return render(request,self.template_name)
    # HTTP POST (only for /login)
    def post(self,request):
        # if login method
        if self.method=='login':
            # Authenticate with Django Framework method 'authenticate'
            user=authenticate(username=request.POST['username'],password=request.POST['password'])
            # if user exists:
            if user is not None:
                # if user is active:
                if user.is_active:
                    # do login with Django Framework method 'login'
                    login(request,user)
                    # redirect to /dashboard
                    return HttpResponseRedirect('/dashboard')
            return render(request,self.template_name,{'error_message':'Login fehlgeschlagen'})
        # if logout
        return HttpResponseRedirect('/login')

"""
HostController
needed for the view of hosts
URLs:
    /dashboard/host
    /dashboard/host/<Host_ID>
"""
class HostController(View):
    template_name='host.html'
    def get(self,request,*args, **kwargs):
        # If host_id was given, return detail_host.html
        # example: dashboard/host/7/
        if 'host_id' in kwargs.keys():
            self.template_name='detail_host.html'
            docker_host=DockerHost.objects.get(id=kwargs['host_id'])
            self.check_if_offline(docker_host)
            return render(request,self.template_name,{'host_active':'active','dashboard_active':'active','docker_host':docker_host})
        # else return list of hosts
        # example: dashboard/host/
        docker_host_list=DockerHost.objects.filter(user=request.user)
        for docker_host in docker_host_list:
            self.check_if_offline(docker_host)
        return render(request, self.template_name,{'docker_host_list':docker_host_list,'host_active':'active','dashboard_active':'active'})
#    else:
#        docker_host=DockerHost.objects.all()
#        return render(request, 'host_detail.html',{'docker_host':docker_host})
    def post(self,request,*args,**kwargs):
        docker_host=DockerHost(name=request.POST['hostname'],description=request.POST['hostdescription'],user=request.user,api_key="",status='offline')
        # generate 128 character API Key
        for _ in range(32):
            docker_host.api_key+=random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits)
        docker_host.save()
        return HttpResponseRedirect('/dashboard/host')
    def check_if_offline(self,docker_host):
        # update status if host is offline
        # this is done here to not have a scheduled job do it everytime
        # if status was longer than 15 minutes ago, update status
        # 15 minutes = 900 seconds
        now=timezone.now()
        if (now - docker_host.last_update).seconds > 900:
            self.update_status(docker_host,'offline')
    def get_all(self,user):
        return DockerHost.objects.filter(user=user)
    def update_status(self,docker_host,status):
        if docker_host.status != status:
            host_status=HostStatusHistory(status_before=docker_host.status,status_after=status,docker_host=docker_host)
            host_status.save()
        docker_host.status=status
        docker_host.save()

    def check_api_key(self,api_key):
        docker_host=DockerHost.objects.get(api_key=api_key)
        if docker_host:
            return docker_host

"""
ContainerController
needed for the view of containers
URLs:
    /dashboard/container
    /dashboard/container/<Container_ID>
"""
class ContainerController(View):
    template_name='container.html'
    def get(self,request,*args,**kwargs):
        if 'container_id' in kwargs.keys():
            self.template_name='detail_container.html'
            docker_container=DockerContainer.objects.get(id=kwargs['container_id'])
            return render(request,self.template_name,{'container_active':'active','dashboard_active':'active','docker_container':docker_container})
        docker_host_list=HostController().get_all(request.user)
        docker_container_list=self.get_all(request.user)
        return render(request,self.template_name,{'container_active':'active','dashboard_active':'active','docker_host_list':docker_host_list,'docker_container_list':docker_container_list})
    def post(self,request):
        docker_host=DockerHost.objects.get(id=request.POST['containerhost'])
        docker_container=DockerContainer(name=request.POST['containername'],description=request.POST['containerdescription'],image=request.POST['containerimage'],ports=request.POST['containerport'],status='none',docker_host=docker_host)
        docker_container.save()
        # now create the tasks
        # first pull the image
        task_template=TaskTemplate.objects.get(name='pull')
        task=Task(task_template=task_template,docker_container=docker_container)
        task.save()
        # afterwards create the container
        task_template=TaskTemplate.objects.get(name='create')
        task=Task(task_template=task_template,docker_container=docker_container)
        task.save()
        return HttpResponseRedirect('/dashboard/container')
    def delete(self,request):
        return HttpResponse("test")
    def get_all(self,user):
        docker_container_list=list()
        for docker_host in DockerHost.objects.filter(user=user):
           for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
              docker_container_list.append(docker_container)
        return docker_container_list


"""
TaskController
needed for the view of tasks
URLs:
    /dashboard/task
"""
class TaskController(View):
    # default template
    template_name='task.html'
    # context directory to give to view
    context={'task_active':'active','dashboard_active':'active'}
    def get(self,request):
        # get all docker hosts of user
        docker_host_list=HostController().get_all(request.user)
        # get all Docker Containers of every docker host
        docker_container_list=ContainerController().get_all(request.user)
        # get all Tasks for every DockerHost
        task_list=self.get_all_for_user(request.user)
        # add every list to the context, task to show them, hosts and containers for the filter
        self.context['task_list']=task_list
        self.context['docker_container_list']=docker_container_list
        self.context['docker_host_list']=docker_host_list
        # render template with context
        return render(request,self.template_name,self.context)
    def get_all_for_user(self,user):
        task_list=list()
        for docker_container in ContainerController().get_all(user):
            for task in Task.objects.filter(docker_container=docker_container):
                task_list.append(task)
        return task_list
    def get_all_for_docker_host(self,docker_host):
        task_list=list()
        for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
            for task in Task.objects.filter(docker_container=docker_container):
                task_list.append(task)
        return task_list
    def get_next_task(self,docker_host):
        try:
            return self.get_all_for_docker_host(docker_host)[0]
        except(IndexError):
            return None


"""
ApiController
needed for the API
URLs:
    /api
"""
class ApiController(View):
    # HTTP GET
    def get(self,request):
        # 403 (Forbidden) bei GET
#        return HttpResponse('403')
         a=HostController()
         dh=DockerHost.objects.get(id=1)
         return HttpResponse(a.get_api_key(dh))
    # HTTP POST
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
            docker_host=HostController().check_api_key(json_request['api_key'])
        except(ValueError,KeyError):
            return HttpResponse("403")
        if docker_host and 'data' in json_request.keys():
            HostController().update_status(docker_host,'online')
            if request.path=='/api/poll/':
                # write data
                # self.update_containers(json_request['data'])
#                return HttpResponse(json_request['data'])
                task=TaskController().get_next_task(docker_host)
                while not task:
                    time.sleep(5)
                    task=TaskController().get_next_task(docker_host)
                return HttpResponse(json.dumps({'data':task.task_template.command.replace("@@IMAGE@@",task.docker_container.image)}))
            elif 'task_id' in kwargs.keys():
                return HttpResponse(json_request['data'])
            else:
                return HttpResponse("403")
        else:
            return HttpResponse("403")



"""
StatusHistoryController
needed for the status history view
URLs:
    /dashboard/history
"""
class StatusHistoryController(View):
    template_name='statushistory.html'
    context={'statushistory_active':'active','dashboard_active':'active'}
    def get(self,request):
        docker_host_list=DockerHost.objects.filter(user=request.user)
        docker_container_list=list()
        for docker_host in docker_host_list:
            for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
                docker_container_list.append(docker_container)
        host_statushistory=list()
        for docker_host in docker_host_list:
            for host_status in HostStatusHistory.objects.filter(docker_host=docker_host):
                host_statushistory.append(host_status)
        container_statushistory=list()
        for docker_container in docker_container_list:
            for container_status in ContainerstatusHistory.objects.filter(docker_container=docker_container):
                container_statushistory.append(container_status)
        # fill directory context
        self.context['docker_host_list']=docker_host_list
        self.context['docker_container_list']=docker_container_list
        self.context['container_statushistory']=container_statushistory
        self.context['host_statushistory']=host_statushistory
        return render(request,self.template_name,self.context)

"""
AccountController
needed for the account view
URLs:
    /account
"""
class AccountController(View):
    template_name='account.html'
    def get(self,request):
        return render(request, self.template_name,{'user':request.user,'account_active':'active'})
