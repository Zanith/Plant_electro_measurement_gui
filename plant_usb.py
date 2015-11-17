import logging

import usb.backend.libusb1 as libusb1
import usb.core
import usb.util

__author__ = 'Kyle V Lopin'

VENDOR_ID = 0x04B4
PRODUCT_ID = 0x8051


class PlantUSB(object):
    def __init__(self):
        # attempt to find the PSoC plant electrophys device
        test = libusb1.get_backend()
        print test
        print 'test'
        self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID, backend=libusb1.get_backend())

        if self.device is None:
            print ValueError("Device not found")
        else:
            logging.info("Device found")

        # set the active configuration, pyUSB handles the details
        self.device.set_configuration()
        logging.error("fix above")

        # set the different interfaces and endpoints of the device, see device API for documentation
        usb_config = self.device.get_active_configuration()

        # the communication is on the first interface (0) and the second alternate setting (1)
        communication_interface = usb_config[(0, 1)]

        self.ep_send_info = communication_interface[1]  # the OUT endpoint is EP2
        self.ep_get_info = communication_interface[0]  # the IN endpoint is EP1

        # the communication is on the first interface (0) and the third alternate setting (2)
        data_interface = usb_config[(0, 2)]
        self.ep_get_data = data_interface[0]  # the IN endpoint for ISO data transfer is the 0 EP of interface 0,2
        self.device.set_interface_altsetting(interface=0, alternate_setting=1)

    def send_message(self, message):
        logging.info("sending message: %s", message)
        self.device.set_interface_altsetting(interface=0, alternate_setting=1)
        self.ep_send_info.write(message)  # write to the corrent endpoint after the proper alt setting is set
        # self.device.write(2, message)  # write to the second endpoint of the alt setting 1

    def read_usb(self):
        count = self.inWaiting()
        print 'count: ', count
        usb_input = self.read(count)
        usb_bytes = []
        for byte in usb_input:
            usb_bytes.append(ord(byte))
        nums = convert_int8_int16(usb_bytes)
        return nums


def convert_int8_int16(_array):
    new_array = [0]*(len(_array)/2)
    for i in range(len(_array)/2):
        new_array[i] = (_array.pop(0) + _array.pop(0)*256.)
    return new_array


