# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
This implementation does its best to follow the Robert Martin's Clean code guidelines.
The comments follows the Google Python Style Guide:
    https://github.com/google/styleguide/blob/gh-pages/pyguide.md
"""

__copyright__ = 'Copyright 2021, FCRLab at University of Messina'
__author__ = 'Lorenzo Carnevale <lcarnevale@unime.it>'
__credits__ = ''
__description__ = 'Meter the Raspberry Pi resources (cpu, mem, net) and power consumption.'


import os
import yaml
import argparse
from writer import Writer
from reader import Reader
from threading import Lock


def main():
    description = ('%s\n%s' % (__author__, __description__))
    epilog = ('%s\n%s' % (__credits__, __copyright__))
    parser = argparse.ArgumentParser(
        description = description,
        epilog = epilog
    )

    parser.add_argument('-c', '--config',
                        dest='config',
                        help='YAML configuration file',
                        type=str,
                        required=True)

    parser.add_argument('-r', '--rate',
                        dest='sampling_rate',
                        help='Sample sensors data any X seconds.',
                        type=int, default=1)

    parser.add_argument('-v', '--verbosity',
                        dest='verbosity',
                        help='Logging verbosity level',
                        action="store_true")

    options = parser.parse_args()
    sampling_rate = options.sampling_rate
    verbosity = options.verbosity
    logdir_name = 'log'
    mutex = Lock()

    with open(options.config) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if not os.path.exists(logdir_name):
        os.makedirs(logdir_name)
    
    writer = setup_writer(sampling_rate, mutex, verbosity)
    reader = setup_reader(config['mqtt'], mutex, verbosity)
    writer.start()
    reader.start()

def setup_writer(sampling_rate, mutex, verbosity):
    writer = Writer(sampling_rate, mutex, verbosity)
    writer.setup()
    return writer

def setup_reader(config, mutex, verbosity):
    reader = Reader(config['host'], config['port'],
        config['topics'], mutex, verbosity)
    reader.setup()
    return reader


if __name__ == "__main__":
    main()