FROM python:2

RUN apt-get update && apt-get upgrade -y && \
    apt-get -y install apt-utils \
    supervisor

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /usr/src/app

COPY * ./
COPY docker/supervisord.conf /etc/supervisor/supervisord.conf

RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

EXPOSE 8080

ENTRYPOINT  ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
