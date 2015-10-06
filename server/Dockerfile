FROM python
COPY requirements.txt / 
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install cron -y
RUN echo "*/15 * * * * root python /endoma/manage.py check_hosts" > /etc/cron.d/endoma
COPY endoma /endoma
EXPOSE 8000
WORKDIR /endoma
CMD cron && python manage.py runserver 0.0.0.0:8000
