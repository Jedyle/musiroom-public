FROM python:3.6.9-buster as base

RUN apt-get update -y
RUN apt-get -y install libpq-dev gcc

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/

WORKDIR /app
RUN pip install --upgrade pip==19.3.1 setuptools==45
RUN pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000

FROM base as prod

COPY ./lamusitheque/ /app/
RUN pip install gunicorn==20.1.0
CMD python manage.py collectstatic --no-input && python manage.py migrate && gunicorn lamusitheque.wsgi:application --bind 0.0.0.0:8000 --workers=3 --threads=2

