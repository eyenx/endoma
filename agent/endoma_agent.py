#!/bin/env python
# imports
import docker
import json
import requests
import time

api_url='http://localhost:8080/api/'
timeout=60
api_key='vlQpLavv0UWAFSlBKH75fhhQqVe2XLbn'
docker_client=docker.Client(base_url='unix://var/run/docker.sock')

while True:
    containers=docker_client.containers(all=True)
    data={'api_key':api_key,'data':containers}
    headers={'content-type':'application/json'}
    try:
        response=requests.post(api_url+'poll/',data=json.dumps(data),headers=headers,timeout=timeout)
        print(response.text)
        response_json=json.loads(response.text)
    except(requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
        pass
    time.sleep(5)
