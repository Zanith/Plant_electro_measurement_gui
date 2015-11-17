__author__ = 'Kyle Vitautas Lopin'


import logging
import Tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg as NavToolbar


class PyplotEmbed(tk.Frame):
    """
    Class that will make a tkinter frame with a matplotlib plot area embedded in the frame
    """
    def __init__(self, root, toolbox_frame, plt_props, _master_frame):
        """
        Initialize the class with a parent of tkinter Frame and embed a pyplot graph in it
        The class also will have a list to hold the data series that is displayed
        :param toolbox_frame: tkinter frame that the toolbox can be shown in
        :param plt_props: properties of the pyplot
        :param _master_frame: the frame that is the master to this frame
        :return:
        """
        self.displayed = False
        tk.Frame.__init__(self, master=_master_frame)  # initialize with the parent class
        self.master = _master_frame
        self.label_instance = ""
        """ Make an area to graph the data """
        self.graph_area = tk.Frame(self)

        """ initiate the pyplot area """
        self.init_graph_area(plt_props, toolbox_frame)
        self.toolbar_status = False

    def init_graph_area(self, plt_props, toolbox_frame):
        """
        take the tkinter Frame (self) and embed a pyplot figure into it
        :param plt_props: dictionary of properties of the pyplot
        :return: bind figure and axis to this instance
        """
        self.graph_area.figure_bed = plt.figure(figsize=(7, 4))
        self.graph_area.axis = plt.subplot(111)
        # self.graph_area.axis.set_autoscalex_on(True)
        # self.graph_area.axis.set_autoscaley_on(True)
        self.lines, = self.graph_area.axis.plot([], [])
        self.graph_area.axis.format_coord = lambda x, y: ""  # remove the coordinates in the toolbox
        """ go through the plot properties and apply each one that is listed """
        for key, value in plt_props.iteritems():
            eval("plt." + key + "(" + value + ")")
        # """ get the limits of the x axis from the parameters if they are not in the properties """
        # if "xlim" not in plt_props:
        #     plt.xlim(self.params['low_cv_voltage'], self.params['high_cv_voltage'])
        # plt.ylim(0, 2)
        """ format the graph area, make the canvas and show it """
        self.graph_area.figure_bed.set_facecolor('white')
        self.graph_area.canvas = FigureCanvasTkAgg(self.graph_area.figure_bed, master=self)
        self.graph_area.canvas._tkcanvas.config(highlightthickness=0)
        """ Make a binding for the user to change the data legend """
        # uncomment below to start making a data legend editor
        # self.graph_area.canvas.mpl_connect('button_press_event', self.legend_handler)
        """ Make the toolbar and then unpack it.  allow the user to display or remove it later """
        self.toolbar = NavToolbar(self.graph_area.canvas, toolbox_frame)
        self.toolbar.pack_forget()

        self.graph_area.canvas.draw()
        self.graph_area.canvas.get_tk_widget().pack(side='top', fill=tk.BOTH, expand=1)

    def update_graph(self, x, y):
        # print 'len x:', len(x), x[0], x[-1]
        # print 'len y:', len(y), y[0], y[-1]
        logging.info("Max input: %i, min input: %i", max(y), min(y))
        _x = x[:len(y)]

        self.lines.set_xdata(_x[-10000:])
        self.lines.set_ydata(y[-10000:])
        self.graph_area.axis.relim()
        self.graph_area.axis.autoscale_view()

        self.graph_area.canvas.draw()  # update the canvas where the data is being shown
