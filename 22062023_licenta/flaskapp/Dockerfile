FROM python:3.7.2-alpine

WORKDIR /flaskapp

ADD . /flaskapp

RUN \
 apk add --no-cache build-base &&\
 apk add --no-cache bash && \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev linux-headers && \
 apk add --no-cache git

RUN pip install --upgrade pip
RUN apk add --no-cache g++ make openssl-dev libffi-dev python3-dev 
RUN apk add --update alpine-sdk 

RUN pip install -r requirements.txt
RUN pip uninstall psycopg2
RUN pip install --no-binary :all: psycopg2

RUN apk add --no-cache curl \
    && curl https://get.helm.sh/helm-v3.7.0-linux-amd64.tar.gz -o helm.tar.gz \
    && tar -zxvf helm.tar.gz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && rm -rf linux-amd64 helm.tar.gz \
    && helm plugin install https://github.com/chartmuseum/helm-push


ENV POSTGRES_DB=ctfplatformdb \
    POSTGRES_USER=admin \
    POSTGRES_PASSWORD=admin \
    PATH="/usr/local/bin/helm:$PATH" \
    HELM_EXPERIMENTAL_OCI=1 \
    HELM_TLS_VERIFY=0

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
#CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0:8080"]