# syntax=docker/dockerfile:1
FROM python:3.6-buster

RUN apt-get update -y
RUN apt-get -y install libpq-dev gcc

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /code/
COPY ./lamusitheque/ /code/

WORKDIR /code
RUN pip install --upgrade pip==19.3.1 setuptools==45
RUN pip install -r requirements.txt


RUN pip install gunicorn==20.1.0
CMD python manage.py collectstatic --no-input && python manage.py migrate && gunicorn lamusitheque.wsgi:application --bind 0.0.0.0:8000

