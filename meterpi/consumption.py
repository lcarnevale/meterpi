#!/usr/bin/env python
import time
from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.1


def read():
    ina = INA219(SHUNT_OHMS)
    ina.configure()

    while True:
        print("Bus Voltage: %.3f V" % ina.voltage())
        try:
            print("Bus Current: %.3f mA" % ina.current())
            print("Power: %.3f mW" % ina.power())
            print("Shunt voltage: %.3f mV" % ina.shunt_voltage())
        except DeviceRangeError as e:
            # Current out of device range with specified shunt resistor
            print(e)
        print("####")
        time.sleep(1)



if __name__ == "__main__":
    read()