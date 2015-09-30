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
    """
    Custom Methods of HostController
    """
    # get all docker_hosts of a given user
    def get_all(self,user):
        return DockerHost.objects.filter(user=user)
    # update the status of a given docker_host
    def update_status(self,docker_host,status):
        # if the status given differs, create a new statushistory record
        if docker_host.status != status:
            host_status=HostStatusHistory(status_before=docker_host.status,status_after=status,docker_host=docker_host)
            host_status.save()
        # set the status
        docker_host.status=status
        # save changes
        docker_host.save()
    # check if the given api exists
    def check_api_key(self,api_key):
        # TODO
        # catch DoesNotExist here
        docker_host=DockerHost.objects.filter(api_key=api_key).first()
        # if there is a host with that api_key, return it
        if docker_host:
            return docker_host
    # check docker version and update it if changed
    def check_docker_version(self,docker_host,version):
        if version != docker_host.docker_version:
            docker_host.docker_version=version
            docker_host.save()

"""
ContainerController
needed for the view of containers
URLs:
    /dashboard/container
    /dashboard/container/<Container_ID>
"""
class ContainerController(View):
    # default tamplate
    template_name='container.html'
    # context used for views
    context={'container_active':'active','dashboard_active':'active'}
    # HTTP GET
    def get(self,request,*args,**kwargs):
        # if container_id is given, return detail view
        if 'container_id' in kwargs.keys():
            self.template_name='detail_container.html'
            self.context['docker_container']=DockerContainer.objects.get(id=kwargs['container_id'])
            return render(request,self.template_name,self.context)
        # else return list of docker containers
        self.context['docker_host_list']=HostController().get_all(request.user)
        self.context['docker_container_list']=self.get_all(request.user)
        return render(request,self.template_name,self.context)
    # HTTP POST (New Container)
    def post(self,request):
        # get given DockerHost
        docker_host=DockerHost.objects.get(id=request.POST['containerhost'])
        # create new docker_container
        docker_container=DockerContainer(name=request.POST['containername'],description=request.POST['containerdescription'],image=request.POST['containerimage'],ports=request.POST['containerport'],status='none',docker_host=docker_host)
        # save it to the database
        docker_container.save()
        # now create the tasks
        # first pull the image
        task_template=TaskTemplate.objects.get(name='pull')
        task=Task(task_template=task_template,docker_container=docker_container,status='Ready')
        task.save()
        # afterwards create the container
        task_template=TaskTemplate.objects.get(name='create')
        task=Task(task_template=task_template,docker_container=docker_container,status='Ready')
        task.save()
        # redirect to the container view
        return HttpResponseRedirect('/dashboard/container')
    # HTTP DELETE (used for deletion of containers)
    # TODO
    def delete(self,request,*args,**kwargs):
        return HttpResponse("403")
    # HTTP PUT
    # used for start and stop
    def put(self,request,*args,**kwargs):
        if "container_id" in kwargs.keys():
            try:
                request_json=json.loads(request.body.decode('utf-8'))
                if 'action' in request_json.keys():
                    # create task with given action (start or stop)
                    task=Task(task_template=TaskTemplate.objects.get(name=request_json['action']),docker_container=DockerContainer.objects.get(id=kwargs['container_id']),status='Ready')
                    task.save()
                    return HttpResponse()
            except(KeyError,ValueError):
                return HttpResponse("403")
        return HttpResponse("403")
    """
    custom methods of ContainerController
    """
    # Get all containers of given user
    def get_all(self,user):
        # instantiate a list
        docker_container_list=list()
        # for every docker_host of the user
        for docker_host in DockerHost.objects.filter(user=user):
            # for every docker_container of that host
           for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
               # add this container to the list
               docker_container_list.append(docker_container)
        # return the list
        return docker_container_list
    def get_by_container_id(self,container_id):
        return DockerContainer.objects.filter(container_id=container_id).first()
    def update_status(self,docker_container,status):
        # if the status given differs, create a new statushistory record
        if docker_container.status != status:
            container_status=ContainerstatusHistory(status_before=docker_container.status,status_after=status,docker_container=docker_container)
            container_status.save()
        # set the status
        docker_container.status=status
        # save changes
        docker_container.save()


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
    # HTTP GET
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
    """
    Custom methods of TaskController
    """
    def get_all_for_user(self,user):
        task_list=list()
        for docker_container in ContainerController().get_all(user):
            for task in Task.objects.filter(docker_container=docker_container):
                task_list.append(task)
        return task_list
    def get_all_for_docker_host(self,docker_host):
        task_list=list()
        for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
            for task in Task.objects.filter(docker_container=docker_container).order_by('id'):
                task_list.append(task)
        return task_list
    def get_next_task(self,docker_host):
        for task in self.get_all_for_docker_host(docker_host):
            if task.status=="Ready":
                return task
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
            # if the requests is on /api/poll
            if request.path=='/api/poll/':
                # get version of docker and update if needed
                HostController().check_docker_version(docker_host,json_request['data']['info']['Version'])
                # update containers data
                self.update_containers(json_request['data']['containers'])
                # get next Task
                task=TaskController().get_next_task(docker_host)
                # if there is no task ready
                while not task:
                    # sleep for 5 seconds
                    time.sleep(5)
                    # try again
                    task=TaskController().get_next_task(docker_host)
                # if there is a task, return it to the agent
                # but first replace the tags
                command=task.task_template.command.replace('@@IMAGE@@','"'+task.docker_container.image+':latest"')
                command=command.replace('@@CONTAINERID@@','"'+task.docker_container.container_id+'"')
                return HttpResponse(json.dumps({'data':{'task_id':task.id,'command':command}}))
            # if the request gives a task_id
            elif 'task_id' in kwargs.keys():
                # get results from request
                task=Task.objects.get(id=kwargs['task_id'])
                self.check_result(json_request['data'],task)
                # in all other cases, return HTTP 403
                return HttpResponse("OK")
            else:
                return HttpResponse("403")
        # in all other cases, return HTTP 403
        else:
            return HttpResponse("403")
    """
    Custom methods of APIController
    """
    def update_containers(self,data):
        # for every given docker container
        for container in data:
        # check if it is in our database
            docker_container=ContainerController().get_by_container_id(container['Id'])
            if docker_container:
            # update its status
            #  two possible status:
            #  Up about 1 hour = "Running"
            #  Exited 5 seconds ago = "Stopped"
            #  Created = "Stopped"
                if container['Status'].startswith('Up '):
                    ContainerController().update_status(docker_container,'Running')
                else:
                    ContainerController().update_status(docker_container,'Stopped')
    # erhaltenes Result entsprechend interpretieren und status speichern
    def check_result(self,data,task):
        task_type=task.task_template.name
        docker_container=task.docker_container
        task.status='Failed'
        if data!='Failed':
            if task_type == 'pull':
                try:
                    last_line=data.split("\r\n")[-2]
                    result_json=json.loads(last_line)
                    if "Status: Downloaded newer image for" in result_json["status"] or "Status: Image is up to date" in result_json["status"]:
                        task.status="Success"
                except(ValueError,KeyError):
                    pass
            elif task_type == 'create':
                try:
                    # write Id to container
                    docker_container.container_id=data['Id']
                    docker_container.save()
                    task.status='Success'
                except(ValueError,KeyError):
                    pass
            elif task_type == 'start' or task_type == 'stop':
                if data==None:
                    task.status='Success'
        # save it
        task.save()




"""
StatusHistoryController
needed for the status history view
URLs:
    /dashboard/history
"""
class StatusHistoryController(View):
    # default template
    template_name='statushistory.html'
    # context used for the view
    context={'statushistory_active':'active','dashboard_active':'active'}
    def get(self,request):
        docker_host_list=HostController().get_all(request.user)
        docker_container_list=ContainerController().get_all(request.user)
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
    # default tamplate
    template_name='account.html'
    # context used for the view
    context={'account_active':'active'}
    def get(self,request):
        return render(request,self.template_name,self.context)
