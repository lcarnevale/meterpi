# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""Reader class.
This implementation does its best to follow the Robert Martin's Clean code guidelines.
The comments follows the Google Python Style Guide:
    https://github.com/google/styleguide/blob/gh-pages/pyguide.md
"""

__copyright__ = 'Copyright 2021, FCRLab at University of Messina'
__author__ = 'Lorenzo Carnevale <lcarnevale@unime.it>'
__credits__ = ''
__description__ = 'The Reader class reads from the persistent queue and publishes on MQTT topic.'

"""
any X minutes 
    check if queue is not empty
    check if network is on
    connect to network
    connect to mqtt
    dequeue all
    send all
    disconnect mqtt
    disconnect network
"""

import time
import json
import socket
import logging
import schedule
import threading
import persistqueue
import paho.mqtt.client as mqtt


class Reader:

    def __init__(self, host, port, topics, mutex, verbosity):
        self.__host = host
        self.__port = port
        self.__topics = topics
        self.__mutex = mutex
        self.__client_name = '%s-sub' % (socket.gethostname())
        self.__reader = None
        self.__setup_logging(verbosity)

    def __setup_logging(self, verbosity):
        format = "%(asctime)s %(filename)s:%(lineno)d %(levelname)s - %(message)s"
        filename='log/population.log'
        datefmt = "%d/%m/%Y %H:%M:%S"
        level = logging.INFO
        if (verbosity):
            level = logging.DEBUG
        logging.basicConfig(filename=filename, filemode='a', format=format, level=level, datefmt=datefmt)

    
    def setup(self):
        pass


    def start(self):
        schedule.every(10).seconds.do(self.__reader_job, 
            host = self.__host, port = self.__port, topics = self.__topics)

        # TODO: do I have to manage the thread cancelation?
        while True:
            schedule.run_pending()
            time.sleep(1)
        
    def __reader_job(self, host, port, topics):
        logging.info("Ran the reader job")
        self.__mutex.acquire()
        q = persistqueue.SQLiteQueue('data', multithreading=True, auto_commit=True)
        self.__mutex.release()

        # defining the client and callbacks
        client = mqtt.Client(self.__client_name)
        client.on_connect = self.__on_connect
        client.on_disconnect = self.__on_disconnect
        client.on_publish = self.__on_publish

        # client.username_pw_set(username=options.username,password=options.password)
        client.connected_flag = False
        client.loop_start()
        logging.info("connecting to broker ...")
        client.connect(host, port, keepalive=60)
        while not client.connected_flag: # wait in loop
            logging.warning("waiting for connection ...")
            time.sleep(1)

        try:
            while (not q.empty()):
                data = q.get()
                logging.debug("Dequeueing new data")
                client.publish(topics[0], json.dumps(data, default=str))
                logging.debug("Sent new data to topic %s" % (topics[0]))
                time.sleep(0.3)
            logging.debug("The queue is empty")
        except KeyboardInterrupt:
            pass
        client.loop_stop()
        client.disconnect()

    def __on_connect(self, client, _, __, rc):
        """Connection's callback
        The callback used when the client receives a CONNACK response from the server.
        Subscribing to on_connect() means that the connection is renewed when it is lost.
        Args:
            client (obj:'paho.mqtt.client.Client'): the client instance for this callback
            rc (int): is used for checking that the connection was established
        """
        return_code = {
            0: "Connection successful",
            1: "Connection refused – incorrect protocol version",
            2: "Connection refused – invalid client identifier",
            3: "Connection refused – server unavailable",
            4: "Connection refused – bad username or password",
            5: "Connection refused – not authorised",
        }
        if (rc == 0):
            logging.info(return_code[rc])
            client.connected_flag = True
        else:
            logging.error(return_code[rc])
 
    def __on_disconnect(self, client, _, rc):
        """MQTT Disconnection callback
        Args:
            client (obj:'paho.mqtt.client.Client'): the client instance for this callback
            rc (int): is used for checking that the disconnection was done
        """
        logging.info('Disconnection successful %s' % (rc))

    def __on_publish(self, client, _, result):
        """Publish's callback
        The callback for when a PUBLISH message is sent to the server
		Args:
			client(obj:'paho.mqtt.client.Client'): the client instance for this callback;
			result():.
		"""
        logging.debug('Data published')