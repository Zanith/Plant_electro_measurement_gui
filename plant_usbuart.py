import logging
import serial

__author__ = 'Kyle V Lopin'

ADC_RESULT_BITS = 16  # the number of bits the adc REPRESENTS the results in, used to calculate twos compliment
ADC_BIT_RESOLUTION = 12  # adc resolution
ADC_VREF = 2048  # mV reference of the adc (not really the vref changes with different settings but just use
# the gain setting to record those changes)
MAX_BIT_VALUE = 2**ADC_BIT_RESOLUTION


class PlantUSB(serial.Serial):
    def __init__(self, _master):
        serial.Serial.__init__(self,
                               'COM11',
                               baudrate=115200,
                               timeout=0)
        self.master = _master

    def read_usb(self):
        count = self.inWaiting()
        logging.debug('reading usb, got count: %i', count)
        usb_input = self.read(count)
        usb_bytes = []
        for byte in usb_input:
            usb_bytes.append(ord(byte))
        nums = convert_int8_int16(usb_bytes)
        volts = convert_counts_to_volts(nums, self.master.gain)
        return volts


def convert_counts_to_volts(adc_counts, gain):
    volts = [ADC_VREF * (adc_count / MAX_BIT_VALUE) / gain for adc_count in adc_counts]
    print gain
    return volts


def convert_int8_int16(_array):
    new_array = [0]*(len(_array)/2)
    for i in range(len(_array)/2):
        new_array[i] = (_array.pop(0) + _array.pop(0)*256.)
    if new_array:
        new_array = convert_twos_compliment(new_array)
    return new_array


def convert_twos_compliment(_array):
    twos_rollover = 2**(ADC_RESULT_BITS - 1)
    twos_subtract = 2**ADC_RESULT_BITS
    _new_array = [x if x < twos_rollover
                  else (x-twos_subtract) for x in _array]
    return _new_array