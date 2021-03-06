# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""Writer class.
This implementation does its best to follow the Robert Martin's Clean code guidelines.
The comments follows the Google Python Style Guide:
    https://github.com/google/styleguide/blob/gh-pages/pyguide.md
"""

__copyright__ = 'Copyright 2021, FCRLab at University of Messina'
__author__ = 'Lorenzo Carnevale <lcarnevale@unime.it>'
__credits__ = ''
__description__ = 'The Writer class writes into a persistent queue.'


import time
import json
import logging
import threading
import persistqueue
from sensors import Sensors
from datetime import datetime


class Writer:

    def __init__(self, tags, sampling_rate, mutex, verbosity):
        self.__tags = tags
        self.__sampling_rate = sampling_rate
        self.__mutex = mutex
        self.__writer = None
        self.__setup_logging(verbosity)

    def __setup_logging(self, verbosity):
        format = "%(asctime)s %(filename)s:%(lineno)d %(levelname)s - %(message)s"
        filename='log/populate.log'
        datefmt = "%d/%m/%Y %H:%M:%S"
        level = logging.INFO
        if (verbosity):
            level = logging.DEBUG
        logging.basicConfig(filename=filename, filemode='a', format=format, level=level, datefmt=datefmt)


    def setup(self):
        self.__writer = threading.Thread(
            target = self.__writer_job, 
            args = ([self.__tags, self.__sampling_rate])
        )

    def __writer_job(self, tags, sampling_rate):
        # SQLite objects created in a thread can only be used in that same thread.
        self.__mutex.acquire()
        self.__queue = persistqueue.SQLiteQueue('data', multithreading=True, auto_commit=True)
        self.__mutex.release()

        try:
            self.__populate_forever(tags, sampling_rate)
        except KeyboardInterrupt:
            pass

    def __populate_forever(self, tags, sampling_rate=1):
        """Populate the database with sensors data.

        Args:
            sampling_rate (int): rate (in seconds) for sampling the sensors 
                data. It is 1 second by default.
        """
        sensors = Sensors()
        while True:
            try:
                data = self.__get_power_consumption(tags, sensors)
                logging.debug('Collected new data')
                self.__queue.put(data)
                logging.debug('JSON data insert into the queue: %s' % (data))

                data = self.__get_cpu(tags, sensors)
                logging.debug('Collected new data')
                self.__queue.put(data)
                logging.debug('JSON data insert into the queue: %s' % (data))

                data = self.__get_memory(tags, sensors)
                logging.debug('Collected new data')
                self.__queue.put(data)
                logging.debug('JSON data insert into the queue: %s' % (data))

                data = self.__get_network(tags, sensors)
                logging.debug('Collected new data')
                self.__queue.put(data)
                logging.debug('JSON data insert into the queue: %s' % (data))
            except ValueError:
                logging.error('Data collected is malformed. JSON required.')
            except Exception as e:
                logging.error(e)

            time.sleep(sampling_rate)

    def __get_power_consumption(self, tags, sensors):
        data = {
                "measurement": "power_consumption",
                "tags": {
                    "mac_address": sensors.get_MAC(),
                    "pi_model": sensors.get_pi_model()
                },
                "fields": sensors.get_ina219_reading(),
                "time": str(datetime.utcnow())
            }
        data['tags'] = {**data['tags'], **tags}
        return data

    def __get_cpu(self, tags, sensors):
        data =  {
                "measurement": "cpu",
                "tags": {
                    "mac_address": sensors.get_MAC(),
                    "pi_model": sensors.get_pi_model()
                },
                "fields": sensors.get_cpu_reading(),
                "time": str(datetime.utcnow())
            }
        data['tags'] = {**data['tags'], **tags}
        return data

    def __get_memory(self, tags, sensors):
        data =  {
                "measurement": "memory",
                "tags": {
                    "mac_address": sensors.get_MAC(),
                    "pi_model": sensors.get_pi_model()
                },
                "fields": sensors.get_mem_reading(),
                "time": str(datetime.utcnow())
            }
        data['tags'] = {**data['tags'], **tags}
        return data

    def __get_network(self, tags, sensors):
        data =  {
                "measurement": "network",
                "tags": {
                    "mac_address": sensors.get_MAC(),
                    "pi_model": sensors.get_pi_model()
                },
                "fields": sensors.get_net_reading(),
                "time": str(datetime.utcnow())
            }
        data['tags'] = {**data['tags'], **tags}
        return data


    def start(self):
        self.__writer.start()