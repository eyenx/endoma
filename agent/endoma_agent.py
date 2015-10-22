#!/bin/env python
"""
File: endoma_agent.py
Comment: EnDoMa Agent
Project: EnDoMa
Author: Antonio Tauro
"""
# imports
import docker
import json
import requests
import time
# API URL which is to be used (must end with /api/)
api_url='http://HOST:PORT/api/'
# API Key defined by the EnDoMa-Application
api_key='API_KEY'
# request timeout
timeout=60
# Start a new client
docker_client=docker.Client(base_url='unix://var/run/docker.sock')

# run forever
while True:
    # get all containers
    containers=docker_client.containers(all=True)
    # get Docker version
    info=docker_client.version()
    # Create JSON data for HTTP Request
    data={'api_key':api_key,'data':{'info':info,'containers':containers}}
    # set Headers
    headers={'content-type':'application/json'}
    try:
        print('connecting to '+api_url)
        # Send Data to API
        response=requests.post(api_url+'poll/',data=json.dumps(data),headers=headers,timeout=timeout)
        # try to loda Response as JSON
        response_json=json.loads(response.text)
        # get Task ID from Response
        task_id=response_json['data']['task_id']
        print('received Task ID: '+str(task_id))
        # Set Command
        command='docker_client.'+response_json['data']['command']
        # prepare response
        response_data={'api_key':api_key}
        print('trying to exec: '+command)
        try:
            # try to exec command
            response_data['data']=eval(command)
        except(docker.errors.NotFound,requests.exceptions.ConnectionError):
            # set to Failed if Exception occured
            response_data['data']='Failed'

        print('sending result to '+api_url)
        # send result to API
        response=requests.post(api_url+'result/'+str(task_id)+"/",data=json.dumps(response_data),headers=headers,timeout=timeout)


    except(requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError,ValueError,KeyError):
        # if a connectionerror occured, or API isn't returning a JSON data
        print('connection closed, retrying in 5 seconds')
    # wait 5 seconds before reconnecting
    time.sleep(5)
