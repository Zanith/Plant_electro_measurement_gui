import Tkinter as tk
import logging
import serial
import time
import numpy as np

import properties
import tkinter_pyplot
import plant_usbuart

__author__ = 'Kyle V Lopin'

DATA_LIMIT = 4000
PWM_CLOCK = 24000000  # Hz
ADC_GAIN_VALUES = (1, 2, 4, 8, 16, 32, 64, 128)


class PlantElectroGUI(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(module)s %(lineno)d: %(message)s")
        self.parameters = properties.DeviceParameters()
        self.streaming = False
        # self.device = serial.Serial('COM11',
        #                             baudrate=115200,
        #                             timeout=0)
        self.device = plant_usbuart.PlantUSB()
        # initialize a pyplot window to display the data
        self.data = []
        self.time = np.array([0])
        graph_frame = tk.Frame(self)
        graph_frame.pack()
        bottom_frame = tk.Frame(self)
        self.data_graph = tkinter_pyplot.PyplotEmbed(self,
                                                     bottom_frame,
                                                     properties.time_course,
                                                     graph_frame)
        self.data_graph.pack()
        main_frame = tk.Frame(self)
        main_frame.pack()
        options_frame = tk.Frame(main_frame)
        options_frame.pack(side='top')
        left_options_frame = tk.Frame(options_frame)
        left_options_frame.pack(side='left')
        right_option_frame = tk.Frame(options_frame)
        right_option_frame.pack(side='left')
        tk.Label(left_options_frame, text="send to device").pack(side='top')
        usb_input = tk.Entry(left_options_frame)
        usb_input.pack()
        tk.Button(left_options_frame, text="enter",
                  command=lambda: self.send_input(usb_input.get())
                  ).pack()
        tk.Button(left_options_frame, text="read",
                  command=lambda: self.read_usb()
                  ).pack()
        self.streaming_button = tk.Button(left_options_frame, text="Read stream",
                                          command=lambda: self.stream_handler())
        self.streaming_button.pack()
        sample_var = tk.IntVar()
        tk.Label(right_option_frame, text='set sampling rate (kHz)').pack(side='top')
        sample_rate_spinbox = tk.Spinbox(right_option_frame,
                                         from_=0, to=30,
                                         textvariable=sample_var)
        sample_rate_spinbox.pack(side='top')
        tk.Button(right_option_frame, text="update sampling rate",
                  command=lambda: self.set_sample_rate(sample_var.get())
                  ).pack(side='top')
        gain_var = tk.IntVar()
        tk.Label(right_option_frame, text='set gain').pack(side='top')
        gain_spinbox = tk.Spinbox(right_option_frame,
                                  values=ADC_GAIN_VALUES,
                                  textvariable=gain_var)
        gain_spinbox.pack(side='top')
        tk.Button(right_option_frame, text="update gain setting",
                  command=lambda: self.set_gain(gain_var.get())
                  ).pack(side='top')

        sample_stringvar = tk.StringVar()
        bottom_frame.pack()

    def stream_handler(self):
        logging.debug("in stream handler, stream value: %s", self.streaming)
        if self.streaming:  # if already streaming and user hits button, turn off streaming
            self.streaming = False
            # putting anything except 'S' in the first char of the PSoC input will stop the streaming
            self.send_input('T')
            logging.debug("setting streaming to false")
            self.streaming_button.config(text="Read stream", relief="raised")
            _ = self.device.read_usb()  # get out the last bit of data the PSoC loaded in
        else:
            self.read_usb_stream()
            self.streaming = True
            self.streaming_button.config(text="Stop streaming", relief="sunken")

    def read_usb_stream(self):
        logging.debug("reading stream")
        num_reads = 2000  # how many data points the psoc should send to the computer before the program looks for it
        time_to_wait = int(self.parameters.timer_period_time * num_reads * 1000)
        # the 1000 is to convert seconds to millisecs
        print "time to wait: ", time_to_wait, self.parameters.timer_period_time
        self.send_input('S')  # this command will tell the psoc to start streaming
        self.after(time_to_wait, lambda: self.get_and_process_stream(time_to_wait))

    def set_gain(self, _gain):
        logging.info("setting gain to: %s", _gain)
        # first letter is the the adc gain and the second is the configuration chosen
        gain_index = ADC_GAIN_VALUES.index(_gain)
        print gain_index
        choices = ['01', '11', '21', '31', '32', '23', '33', '34']
        # ADC_Gain=(1,   2,   4,     8,   16,   32,   64,    128)
        self.send_input(''.join(['G|', choices[gain_index]]))

    def set_sample_rate(self, new_rate):
        """
        The PSoC's adc timer is a PWM with a 24 MHz clock.  To change the timing of the adc
        you change the period register and send the value in the form of T|XXXXX.  where XXXXX
        is the value to set the register, the numbers must be padded with zeros.
        :param new_rate:
        :return:
        """
        logging.info("setting sampling rate to %i", new_rate)
        register_value = self.convert_rate_to_pwm_register_value(new_rate)
        self.send_input(''.join(['T|','{0:05d}'.format(register_value)]))

    def convert_rate_to_pwm_register_value(self, _user_freq):
        logging.error("fix this here")
        pwm_reg_value = int(float(PWM_CLOCK) / float(_user_freq))
        return pwm_reg_value

    def get_and_process_stream(self, waiting_time):
        print 'time: ', time.time(), waiting_time
        new_data = self.device.read_usb()
        if new_data and self.streaming:
            # self.data = self.data[-DATA_LIMIT:]
            self.data.extend(new_data)
            new_time_stop = self.time[-1] + self.parameters.delta_t * (len(new_data)+1)
            new_time = np.arange(self.time[-1] + self.parameters.delta_t,
                                 new_time_stop,
                                 self.parameters.delta_t)
            print 'len new_time: ', len(new_time), new_time[0], new_time[-1]
            self.time = np.append(self.time, new_time)
            self.time = self.time[:len(self.data)]  # this is a hack, time keeps getting to big for some reason
            self.data_graph.update_graph(self.time, self.data)
        logging.debug("End of get and process stream with streaming value: %s", self.streaming)
        if self.streaming:
            self.after(waiting_time, lambda: self.get_and_process_stream(waiting_time))

    def read_usb2(self):
        count = self.device.inWaiting()
        print 'count: ', count
        usb_input = self.device.read(count)
        usb_bytes = []
        for byte in usb_input:
            usb_bytes.append(ord(byte))
        nums = convert_int8_int16(usb_bytes)
        return nums

    def send_input(self, message):
        print message
        self.device.write(message)
        # self.device.send_message(message)


def convert_int8_int16(_array):
    new_array = [0]*(len(_array)/2)
    for i in range(len(_array)/2):
        new_array[i] = (_array.pop(0) + _array.pop(0)*256.)
    # print 'max new array: ', max(new_array)
    return new_array

if __name__ == '__main__':
    app = PlantElectroGUI()
    app.title("Plant Electrical Activity Measuring Device")
    app.geometry("750x450")
    app.mainloop()
