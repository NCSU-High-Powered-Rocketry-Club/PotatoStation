from digi.xbee.devices import XBeeDevice
import time

device = XBeeDevice("COM16", 9600)
device.open()

while True:
    device.send_data_broadcast("Hello")
    time.sleep(2)
