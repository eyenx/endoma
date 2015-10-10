from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.views.generic import View
# import needed HTTP Classes from django framework
from django.http import HttpResponse,HttpRequest,HttpResponseRedirect,HttpResponseForbidden,JsonResponse
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
        # if index.html and authenticated redirect
        if self.template_name=='index.html' and request.user.is_authenticated():
            return HttpResponseRedirect('/dashboard')
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
        # if already logged in -> redirect
        if request.user.is_authenticated():
            return HttpResponseRedirect('/dashboard')
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
    context={'host_active':'active','dashboard_active':'active'}
    # HTTP GET
    def get(self,request,*args, **kwargs):
        # If host_id was given, return detail_host.html
        # example: dashboard/host/7/
        if 'host_id' in kwargs.keys():
            self.template_name='detail_host.html'
            docker_host=DockerHost.objects.get(id=kwargs['host_id'])
            # check for ownership
            if docker_host.user!=request.user:
                return HttpResponseForbidden()
            self.context['docker_host']=docker_host
            return render(request,self.template_name,self.context)
        # else return list of hosts
        # example: dashboard/host/
        for docker_host in DockerHost.objects.filter(user=request.user):
            # check if docker_host is to delete
            if docker_host.to_delete:
                self.check_if_to_remove(docker_host)
        self.context['docker_host_list']=DockerHost.objects.filter(user=request.user)
        return render(request, self.template_name,self.context)
    # HTTP POST
    def post(self,request,*args,**kwargs):
        docker_host=DockerHost(name=request.POST['hostname'],description=request.POST['hostdescription'],user=request.user,api_key='',status='Offline')
        # generate 128 character API Key
        for _ in range(32):
            docker_host.api_key+=random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits)
        docker_host.save()
        return HttpResponseRedirect('/dashboard/host')
    # HTTP DELETE
    def delete(self,request,*args,**kwargs):
        if 'host_id' in kwargs.keys():
            # get Host
            docker_host=DockerHost.objects.get(id=kwargs['host_id'])
            if docker_host.user!=request.user:
                return HttpResponseForbidden()
            # check for ownership
            if docker_host.user!=request.user:
                return HttpResponseForbidden()
            # delete host
            self.remove(docker_host)
            # delete all docker_containers first
            return HttpResponse()
        return HttpResponseForbidden()
    """
    Custom Methods of HostController
    """
    # check if host should be deleted
    def check_if_to_remove(self,docker_host):
        # if no dockercontainers left
        if not DockerContainer.objects.filter(docker_host=docker_host):
            docker_host.delete()
    # remove host
    def remove(self,docker_host):
        # first mark all container for deletion
        for docker_container in DockerContainer.objects.filter(docker_host=docker_host):
            ContainerController().remove(docker_container)
        docker_host.to_delete=True
        docker_host.save()
    # get all docker_hosts of a given user
    def get_all(self,user):
        return DockerHost.objects.filter(user=user).order_by('id')
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
            self.context['environment_variables']=EnvironmentVariable.objects.filter(docker_container=self.context['docker_container'])
            self.context['links']=Link.objects.filter(source=self.context['docker_container'])
            # check for ownership
            if self.context['docker_container'].docker_host.user!=request.user:
                return HttpResponseForbidden()
            return render(request,self.template_name,self.context)
        # else return list of docker containers
        self.context['docker_host_list']=HostController().get_all(request.user)
        self.context['docker_container_list']=self.get_all(request.user)
        return render(request,self.template_name,self.context)
    # HTTP POST (New Container)
    def post(self,request):
        # get given DockerHost
        docker_host=DockerHost.objects.get(id=request.POST['containerhost'])
        # check for ownership
        if docker_host.user!=request.user:
            return HttpResponseForbidden()
        # create new docker_container
        docker_container=DockerContainer(name=request.POST['containername'],description=request.POST['containerdescription'],image=request.POST['containerimage'],port=request.POST['containerport'],docker_host=docker_host,container_id='',status='')
        # save it to the database
        docker_container.save()
        # create links
        if request.POST['containerlinks']:
            link_list=request.POST['containerlinks'].split(',')
            link_list.pop()
            for link_id in link_list:
                destination_container=DockerContainer.objects.get(id=link_id)
                if not Link.objects.filter(source=docker_container,destination=destination_container):
                    link=Link(source=docker_container,destination=destination_container)
                    link.save()
        # create environment variables
        if request.POST['containervars']:
            var_list=request.POST['containervars'].split(',')
            var_list.pop()
            for var in var_list:
                key=var.split(':')[0]
                value=var.split(':')[1]
                if not EnvironmentVariable.objects.filter(key=key,docker_container=docker_container):
                    environment_variable=EnvironmentVariable(key=key,value=value,docker_container=docker_container)
                    environment_variable.save()
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
    def delete(self,request,*args,**kwargs):
        if 'container_id' in kwargs.keys():
            docker_container=DockerContainer.objects.get(id=kwargs['container_id'])
            # check for ownership
            if docker_container.docker_host.user!=request.user:
                return HttpResponseForbidden()
            self.remove(docker_container)
            return HttpResponseRedirect('/dashboard/container')
        return HttpResponseForbidden()
    # HTTP PUT
    # used for start and stop
    def put(self,request,*args,**kwargs):
        if 'container_id' in kwargs.keys():
            try:
                request_json=json.loads(request.body.decode('utf-8'))
                if 'action' in request_json.keys():
                    docker_container=DockerContainer.objects.get(id=kwargs['container_id'])
                    # check for ownership
                    if docker_container.docker_host.user!=request.user:
                        return HttpResponseForbidden()
                    # create task with given action (start or stop)
                    task=Task(task_template=TaskTemplate.objects.get(name=request_json['action']),docker_container=docker_container,status='Ready')
                    task.save()
                    return HttpResponse()
            except(KeyError,ValueError):
                return HttpResponseForbidden()
        return HttpResponseForbidden()
    """
    custom methods of ContainerController
    """
    # remove container
    def remove(self,docker_container):
        # first check if container has no containerid
        if not docker_container.container_id:
            # delete it right away
            docker_container.delete()
            return
        # mark Container for deletion and create task for deletion on host
        docker_container.to_delete=True
        docker_container.save()
        # first stop
        task_stop=Task(task_template=TaskTemplate.objects.get(name='stop'),docker_container=docker_container,status='Ready')
        task_stop.save()
        # afterwards delete
        task_delete=Task(task_template=TaskTemplate.objects.get(name='delete'),docker_container=docker_container,status='Ready')
        task_delete.save()
    # Get all containers of given user
    def get_all(self,user):
        # return all DockerContainer which are related to the list of DockerHost owned by the user
        return DockerContainer.objects.filter(docker_host__in=DockerHost.objects.filter(user=user)).order_by('id')
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
        # return all Tasks for the user ordered by the id DESC
        return Task.objects.filter(docker_container__in=ContainerController().get_all(user)).order_by('-id')
    def get_next_task(self,docker_host):
        # return the first task for the docker-host which is Ready
        return Task.objects.filter(docker_container__in=DockerContainer.objects.filter(docker_host=docker_host),status='Ready').order_by('id').first()



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
        return HttpResponseForbidden()
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
            return HttpResponseForbidden()
        if docker_host and 'data' in json_request.keys():
            HostController().update_status(docker_host,'Online')
            # if the requests is on /api/poll
            if request.path=='/api/poll/':
                # get version of docker and update if needed
                HostController().check_docker_version(docker_host,json_request['data']['info']['Version'])
                # update containers data
                self.update_containers(json_request['data']['containers'])
                # check for removed containers
                self.check_for_removed_containers(docker_host,json_request['data']['containers'])
                # get next Task
                task=TaskController().get_next_task(docker_host)
                # as long as there is no task ready and the timeout of 60 seconds isn't reached
                # (sleeping for 5 seconds, makes the loop work 12 times)
                loop_count=12
                while not task and loop_count:
                    loop_count-=1
                    if not loop_count:
                        return HttpResponse()
                    # sleep for 5 seconds
                    time.sleep(5)
                    # try again
                    task=TaskController().get_next_task(docker_host)
                # if there is a task, return it to the agent
                # but first replace the tags
                command=task.task_template.command.replace('@@IMAGE@@','"'+task.docker_container.image+':latest"')
                command=command.replace('@@HOST_CONFIG@@',self.create_host_config(task.docker_container))
                command=command.replace('@@PORT@@',task.docker_container.port)
                command=command.replace('@@ENVIRONMENT@@',self.create_environment_variables_list(task.docker_container))
                command=command.replace('@@CONTAINERID@@','"'+task.docker_container.container_id+'"')
                task.status='Sent'
                task.save()
                #return HttpResponse(json.dumps({'data':{'task_id':task.id,'command':command}}))
                return JsonResponse({'data':{'task_id':task.id,'command':command}})
            # if the request gives a task_id
            elif 'task_id' in kwargs.keys():
                # get results from request
                task=Task.objects.get(id=kwargs['task_id'])
                self.check_result(json_request['data'],task)
                # in all other cases, return HTTP 403
                return HttpResponse('OK')
            else:
                return HttpResponseForbidden()
        # in all other cases, return HTTP 403
        else:
            return HttpResponseForbidden()
    """
    Custom methods of APIController
    """
    # create environment variables list
    def create_environment_variables_list(self,docker_container):
        return_string="{"
        environment_variables=EnvironmentVariable.objects.filter(docker_container=docker_container)
        for var in environment_variables:
            return_string+='"'+var.key+'":"'+var.value+'",'
        return_string+="}"
        return return_string


    # create host_config for Task
    def create_host_config(self,docker_container):
        return_string=""
        if docker_container.port:
            return_string+="port_bindings={"+docker_container.port+":"+docker_container.port+"},"
        # get Links for this docker container
        links=Link.objects.filter(source=docker_container)
        if links:
            return_string+='links={'
            for link in links:
                return_string+='"'+link.destination.container_id+'":"'+link.destination.name.replace(' ','_')+'",'
            return_string+='}'
        return return_string
    def check_for_removed_containers(self,docker_host,data):
        container_ids=list()
        for container in data:
            container_ids.append(container['Id'])
        for docker_container in DockerContainer.objects.filter(docker_host=docker_host,to_delete=True):
            if docker_container.container_id not in container_ids:
                docker_container.delete()
    def update_containers(self,data):
        # for every given docker container
        for container in data:
        # check if it is in our database
            docker_container=ContainerController().get_by_container_id(container['Id'])
            if docker_container:
            # update its status
            #  two possible status:
            #  Up about 1 hour = 'Running'
            #  Exited 5 seconds ago = 'Stopped'
            #  Created = 'Stopped'
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
                    last_line=data.split('\r\n')[-2]
                    result_json=json.loads(last_line)
                    if 'Status: Downloaded newer image for' in result_json['status'] or 'Status: Image is up to date' in result_json['status']:
                        task.status='Success'
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
            elif task_type == 'delete':
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
            for host_status in HostStatusHistory.objects.filter(docker_host=docker_host).order_by('id'):
                host_statushistory.append(host_status)
        container_statushistory=list()
        for docker_container in docker_container_list:
            for container_status in ContainerstatusHistory.objects.filter(docker_container=docker_container).order_by('id'):
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
