FROM python:alpine
MAINTAINER Kieran Coldron <kieran@coldron.com>

COPY requirements.txt .

RUN apk add --update py-gunicorn python-dev libffi-dev openssl-dev build-base && \
    pip install -r requirements.txt && \
    apk del build-base && \
    rm -rf /var/cache/apk/*

WORKDIR /usr/src/app

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--config", "deploy/gunicorn_config.py","--chdir","app","app:app"]
