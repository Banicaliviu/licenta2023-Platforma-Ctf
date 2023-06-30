FROM ubuntu

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y apache2

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -qy mysql-server
RUN apt-get -y install php libapache2-mod-php php-mysql vim

RUN usermod -d /var/lib/mysql/ mysql
COPY server-files/app/ /var/www/html
COPY server-files/conf/init.sql /tmp
RUN rm /var/www/html/index.html

RUN echo "ServerName ctf.crimemail.ctfplatform" >> /etc/apache2/apache2.conf
EXPOSE 80

CMD find /var/lib/mysql -type f -exec touch {} \; && \
    service mysql restart && \
    mysql -uroot < /tmp/init.sql && rm /tmp/init.sql && \
    service apache2 start && \
    tail -f /var/log/apache2/*.log

