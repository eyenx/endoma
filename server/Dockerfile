FROM python
COPY requirements.txt / 
COPY task /task
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install cron -y
RUN echo "*/5 * * * * root /task" > /etc/cron.d/endoma
COPY task /task
RUN chmod +x /task
COPY endoma /endoma
EXPOSE 8000
WORKDIR /endoma
CMD env > /env && cron && python manage.py runserver 0.0.0.0:8000
