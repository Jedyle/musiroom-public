FROM python:3.6.9-buster as base

RUN apt-get update -y
RUN apt-get -y install libpq-dev gcc

RUN apt-get update                             \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr           \
 && rm -fr /var/lib/apt/lists/*                \
 && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz | tar xz -C /usr/local/bin \
 && apt-get purge -y ca-certificates curl

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/

WORKDIR /app
RUN pip install --upgrade pip==19.3.1 setuptools==45
RUN pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000

FROM base as prod

COPY ./musiroom/ /app/
RUN pip install gunicorn==20.1.0
CMD python manage.py collectstatic --no-input && python manage.py migrate && gunicorn musiroom.wsgi:application --bind 0.0.0.0:8000 --workers=3 --threads=2

