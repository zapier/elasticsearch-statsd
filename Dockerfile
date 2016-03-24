FROM ubuntu:14.04

RUN apt-get update -y && apt-get install -y python-pip && pip install requests statsd

ADD app.py /app.py

CMD python /app.py
