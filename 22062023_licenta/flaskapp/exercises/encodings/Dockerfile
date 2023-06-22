FROM ubuntu:18.04

COPY file.base32 /app/file.base32
COPY file.base64 /app/file.base64
COPY file.hex /app/file.hex

WORKDIR /

RUN apt-get update && apt-get install -y coreutils \
    && apt-get -y install openssh-server sudo -y \
    && useradd -g root -G sudo -u 1000 test \
    && echo 'test:test' | chpasswd \
    && mkdir /var/run/sshd

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]