#!/bin/bash

# Postgres Root Password
PG_ROOT_PWD=mysecretpassword
# endoma DB User Password
ENDOMA_DB_PWD=endoma_pw
# define tmp file
TMPFILE=/tmp/create_db.sql
# build the endoma_server
echo -e "\n====================================="
echo 1. building the container
echo -e "=====================================\n"
docker build -t endoma_server . 
# start a new database
echo -e "\n====================================="
echo 2. starting the database
echo -e "=====================================\n"
docker run -d --name endoma_db -e POSTGRES_PASSWORD=$PG_ROOT_PWD postgres
# wait for it to initialize
sleep 10
# create tmp file to read
> $TMPFILE
echo CREATE USER endoma WITH PASSWORD \'$ENDOMA_DB_PWD\'\; >> $TMPFILE
echo CREATE DATABASE endoma_db WITH OWNER endoma\; >> $TMPFILE
# create endoma user and database
echo -e "\n====================================="
echo 3. creating user and database
echo -e "=====================================\n"
docker run -i -e PGPASSWORD=$PG_ROOT_PWD --link endoma_db:postgres --rm postgres sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres ' < $TMPFILE
rm $TMPFILE
# create auth tables
echo -e "\n====================================="
echo 4. initializing the database
echo -e "=====================================\n"
docker run -e DB_PASSWORD=$ENDOMA_DB_PWD --link endoma_db:endoma_db endoma_server python manage.py migrate auth
# create other tables
docker run -e DB_PASSWORD=$ENDOMA_DB_PWD --link endoma_db:endoma_db endoma_server python manage.py migrate
# initiate tasktemplate
docker run -e DB_PASSWORD=$ENDOMA_DB_PWD --link endoma_db:endoma_db endoma_server python manage.py init_tasktemplate
# create a super user
echo -e "\n====================================="
echo "5. Please Create a superuser with this command"
echo -e "=====================================\n"
echo docker run -e DB_PASSWORD=$ENDOMA_DB_PWD -ti --link endoma_db:endoma_db endoma_server python manage.py createsuperuser
# output info
echo -e "\n====================================="
echo "7. Start the container with this command" 
echo -e "=====================================\n"
echo docker run -e DB_PASSWORD=$ENDOMA_DB_PWD -d --name endoma_server -p 8000:8000 --link endoma_db:endoma_db endoma_server
