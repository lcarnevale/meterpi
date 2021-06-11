# MeterPi
<img src="https://img.shields.io/badge/python-v3-blue" alt="python-v3-blue">

This project aims monitoring power consumtion and resources (cpu, memory, network) of a Raspberry Pi 3. It uses the reader-writer paradigm for consuming messages.

## How to use it
Clone the repository and build it locally using the Dockerfile. Use the ```build.sh``` script or directly the docker command.
```bash
docker build -t lcarnevale/meterpi .
```

Run the image, defining your configuration directory (i.e. ```/opt/lcarnevale/meterpi```).
```bash
docker run -d --name meterpi \
    -v /opt/lcarnevale/meterpi:/etc/meterpi \
    -v /var/log/lcarnevale:/opt/meterpi/log \
    --device /dev/i2c-1 \
    --net=host \
    lcarnevale/meterpi
```

Use also the option ```--restart unless-stopped ``` if you wanna make it able to start on boot.

## How to debug it
Open the log file for watching what is going on.
```bash
tail -f /var/log/lcarnevale/meterpi.log
```