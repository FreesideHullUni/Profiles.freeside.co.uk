FROM python:3.6-alpine3.6
MAINTAINER Kieran Coldron <kieran@coldron.com>

COPY requirements.txt .

RUN apk add --update python3-dev libffi-dev openssl-dev build-base rust cargo && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r requirements.txt && \
    apk del build-base && \
    rm -rf /var/cache/apk/*

WORKDIR /usr/src/app

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--config", "deploy/gunicorn_config.py","main:app"]
