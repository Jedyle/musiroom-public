FROM python:3.10-buster as base

RUN apt-get update -y
RUN apt-get -y install libpq-dev gcc

RUN apt-get update                             \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr           \
 && rm -fr /var/lib/apt/lists/*                \
 && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz | tar xz -C /usr/local/bin

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/

WORKDIR /app
RUN pip install --upgrade pip==22.0.4 setuptools==61.3.1 wheel==0.37.1
RUN pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000

FROM base as dev
COPY requirements.dev.txt /app/
COPY setup.cfg /app/
COPY conftest.py /app/
RUN pip install -r requirements.dev.txt
CMD python manage.py runserver 0.0.0.0:8000

FROM base as prod

COPY ./musiroom/ /app/
RUN pip install gunicorn==20.1.0
CMD python manage.py collectstatic --no-input && python manage.py migrate && gunicorn musiroom.wsgi:application --bind 0.0.0.0:8000 --workers=3 --threads=2

