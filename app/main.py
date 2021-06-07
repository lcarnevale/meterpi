# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
This implementation does its best to follow the Robert Martin's Clean code guidelines.
The comments follows the Google Python Style Guide:
    https://github.com/google/styleguide/blob/gh-pages/pyguide.md
"""

__copyright__ = 'Copyright 2021, FCRlab at University of Messina'
__author__ = 'Lorenzo Carnevale <lcarnevale@unime.it>'
__credits__ = ''
__description__ = ''

import time
import json
import logging
import argparse
from sensors import Sensors
from datetime import datetime


def main():
    description = ('%s\n%s' % (__author__, __description__))
    epilog = ('%s\n%s' % (__credits__, __copyright__))
    parser = argparse.ArgumentParser(
        description = description,
        epilog = epilog
    )

    # parser.add_argument('-c', '--config',
    #                     dest='config',
    #                     help='YAML configuration file',
    #                     type=str,
    #                     required=True)

    parser.add_argument('-v', '--verbosity',
                        dest='verbosity',
                        help='Logging verbosity level',
                        action="store_true")

    options = parser.parse_args()
    
    sensors = Sensors()
    while True:
        data = {
            "measurement": "",
            "tags": {
                "region": "sicily",
                "city": "messina",
                "mac_address": sensors.get_MAC(),
                "pi_model": sensors.get_pi_model()
            },
            "fields": {
                "power_consumption": sensors.get_ina219_reading(),
                "cpu": sensors.get_cpu_reading(),
                "memory": sensors.get_mem_reading(),
                "network": sensors.get_net_reading()
            },
            "time": datetime.utcnow()
        }
        print(json.dumps(data, indent=4, sort_keys=True, default=str))
        print("TODO: send to MQTT topic.")
        time.sleep(1)


if __name__ == "__main__":
    main()