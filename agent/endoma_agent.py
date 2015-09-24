#!/bin/env python
# imports
import docker
import json
import requests
import time

api_url='http://localhost:8080/api/'
interval=2
api_key='KZvpqPDrrl3aoqWJNJKpSSIaM1tAdO0H'
docker_client=docker.Client(base_url='unix://var/run/docker.sock')

while True:
    containers=docker_client.containers(all=True)
    data={'api_key':api_key,'data':containers}
    headers={'content-type':'application/json'}
    response=requests.post(api_url+'poll/',data=json.dumps(data),headers=headers)
    response_json=json.loads(response.text)
    print(response_json['data'])
    time.sleep(interval)
