FROM python:3.7.2-alpine

WORKDIR /app

ADD ./app /app

RUN \
 apk add --no-cache build-base &&\
 apk add --no-cache bash && \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev linux-headers && \
 apk add --no-cache git

RUN pip install -r requirements.txt

ENV POSTGRES_DB=ctfplatformdb \
    POSTGRES_USER=admin \
    POSTGRES_PASSWORD=admin \
    PATH="/usr/local/bin/helm:$PATH" \
    HELM_EXPERIMENTAL_OCI=1 \
    HELM_TLS_VERIFY=0

CMD ["gunicorn", "--bind", "0.0.0.0:8089", "app:app"]
#CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0:8080"]
