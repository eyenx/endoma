# Enhanced Docker Management

**En**hanced **Do**cker **Ma**nagement ist eine Webapplikation für das Verwalten von Containern, welche mithilfe von Docker bereitgestellt werden.

Die Applikation ist aufgeteilt in ein Server- und Agent-teil.

## Installation WebServer

Vorbedingungen: Docker>=1.8.1

### Vorbereitungen

```
~/endoma/server $ chmod +x build.sh
~/endoma/server $ vim build.sh
```
Folgende Variablen sind anzupassen:
```
# Postgres Root Password
PG_ROOT_PWD=mysecretpassword
# endoma DB User Password
ENDOMA_DB_PWD=endoma_pw
```
### Installation starten
```
~/endoma/server $ ./build.sh
~/endoma/server $ docker run -e DB_PASSWORD=endoma_pw -ti --link endoma_db:endoma_db endoma_server python manage.py createsuperuser
```

### Server starten

```
~/endoma/server$ docker run -e DB_PASSWORD=endoma_pw -d --name endoma_server -p 8000:8000 --link endoma_db:endoma_db endoma_server
```

## Installation Agent

Vorbedingungen: Docker>=1.8.1, docker-py>=1.3.1


### Vorbereitungen

```
~/endoma/agent $ sudo pip install docker-py
~/endoma/agent $ vim endoma_agent.py
```

Folgende Variablen sind anzupassen:

```
# API URL which is to be used (must end with /api/)
api_url='http://HOST:PORT/api/'
# API Key defined by the EnDoMa-Application
api_key='API_KEY'
```

### Agent starten

```
~/endoma/agent $ python endoma_agent.py
```
