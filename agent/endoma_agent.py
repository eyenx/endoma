#!/bin/env python
# imports
import docker
import json
import requests
import time

api_url='http://localhost:8080/api/'
timeout=60
api_key='0hH1WdHIiOUSaOvh13GZ2GVrz74ZFGS6'
docker_client=docker.Client(base_url='unix://var/run/docker.sock')

while True:
    containers=docker_client.containers(all=True)
    info=docker_client.version()
    data={'api_key':api_key,'data':{'info':info,'containers':containers}}
    headers={'content-type':'application/json'}
    try:
        print('connecting to '+api_url)
        response=requests.post(api_url+'poll/',data=json.dumps(data),headers=headers,timeout=timeout)
        response_json=json.loads(response.text)
        task_id=response_json['data']['task_id']
        print('received Task ID: '+str(task_id))
        command='docker_client.'+response_json['data']['command']
        # prepare response
        response_data={'api_key':api_key}
        # try to exec
        print('trying to exec: '+command)
        try:
            response_data['data']=eval(command)
        except(docker.errors.NotFound,requests.exceptions.ConnectionError):
            response_data['data']='Failed'

        # send result to API
        print('sending result to '+api_url)
        response=requests.post(api_url+'result/'+str(task_id)+"/",data=json.dumps(response_data),headers=headers,timeout=timeout)


    except(requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError,ValueError,KeyError):
        print('connection closed, retrying in 5 seconds')
    time.sleep(5)

