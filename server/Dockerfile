FROM python
COPY requirements.txt / 
RUN pip install -r requirements.txt
COPY endoma /endoma
COPY start /start
COPY job /job
RUN chmod +x /start
RUN chmod +x /job
EXPOSE 8000
WORKDIR /endoma
CMD /start
