FROM arm32v7/alpine:latest
LABEL maintainer="Lorenzo Carnevale"
LABEL email="lcarnevale@unime.it"

COPY requirements.txt /opt/meterpi/requirements.txt
WORKDIR /opt/meterpi

RUN apk update && \
	apk add python3 python3-dev py3-pip && \
	apk add --no-cache gcc musl-dev linux-headers && \
	pip3 install --upgrade pip && \
	pip3 install -r requirements.txt && \
	rm -rf /var/cache/apk/* && \
	rm -rf /tmp/*

COPY meterpi /opt/meterpi

CMD ["sh", "-c", "python3 meterpi.py -v -c /etc/meterpi/config.yaml"]