__author__ = 'Kyle Vitautas Lopin'


time_course = {'xlabel': "'time (mS)'",
               'ylabel': "'voltage (mV)'",
               'xlim': "[0, 200]",
               'ylim': "[-.1,1]",
               'title': "'Amperometry time course'",
               'subplots_adjust': "bottom=0.15, left=0.12"}


class Parameters(object):
    def __init__(self):
        self.pwm_clock = 24000000  # look up in datasheet of psoc

