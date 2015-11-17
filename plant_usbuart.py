import logging
import serial

__author__ = 'Kyle V Lopin'

ADC_BITS = 16


class PlantUSB(serial.Serial):
    def __init__(self):
        serial.Serial.__init__(self,
                               'COM11',
                               baudrate=115200,
                               timeout=0)

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
    if new_array:
        new_array = convert_twos_compliment(new_array)
    return new_array


def convert_twos_compliment(_array):
    print "twos converter: ", _array[0]
    twos_rollover = 2**(ADC_BITS - 1)
    twos_subtract = 2**ADC_BITS
    _new_array = [x if x < twos_rollover
                  else (x-twos_subtract) for x in _array]
    print 'converted to: ', _new_array[0]
    return _new_array