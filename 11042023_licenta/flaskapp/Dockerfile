FROM python:3.7.2-alpine

WORKDIR /flaskapp

ADD . /flaskapp

RUN \
 apk add --no-cache build-base &&\
 apk add --no-cache bash && \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev linux-headers

RUN pip install -r requirements.txt

ENV POSTGRES_DB=ctfplatformdb POSTGRES_USER=admin POSTGRES_PASSWORD=admin 

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
#CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0:8080"]