__author__ = 'Kyle Vitautas Lopin'


time_course = {'xlabel': "'Time (S)'",
               'ylabel': "'Voltage (mV)'",
               # 'xlim': "[0, 200]",
               # 'ylim': "[-.1,1]",
               # 'title': "'Amperometry time course'",
               'subplots_adjust': "bottom=0.15, left=0.15"}


class DeviceParameters(object):
    def __init__(self):
        # pwm is the pwm that sets off the adc isr
        self.timer_clock = 24000000  # (Hz) look up in datasheet of psoc
        self.timer_period_reg_value = 20000  # uint16 value in the period register of the pwm initially
        self.timer_period_time = float(self.timer_period_reg_value) / float(self.timer_clock)  # second
        self.delta_t = self.timer_period_time
