
"""
List of functions intended to support the Jupyter Notebooks, encapsulating code that the user
don't need to access in a normal view.

Set of functions invoked in OpenSignals Tools Notebooks to present some graphical results.
These function are only designed for a single end, but we made them available to the user if he
want to explore graphical functionalities with practical examples.

Bokeh is the base package of this module, ensuring an interactive and attractive data plotting
integrable in web pages and applications like our Jupyter Notebooks.

Available Functions
-------------------
[Public]

css_style_apply
    Function that apply the css configurations to the Jupyter Notebook pages.
plot_compare_act_config
    With this function is generated a gridplot showing the differences in muscular activation
    detection results when the input arguments of detect_emg_activations function are changed.
plot_median_freq_evol
    Representation of a plot that shows the median power frequency evolution time series of
    an acquired EMG signal.
plot_sample_rate_compare
    Gridplot showing differences in ECG signal morphology as a consequence of changing the
    acquisition sampling rate.
acquire_subsamples_gp1 [Old Version]
    Graphical function that shows the differences in ECG signals accordingly to the chosen
    sampling rate.
plot_resp_slow
    Function invoked in order to present the RIP signal together the rectangular signal that
    identifies the inhalation and exhalation stages.
plot_resp_diff
    Similar do plot_resp_slow but in this particular case is presented the 1st derivative of RIP
    signal instead of the orignal acquired data.


Available Functions
-------------------
[Private]

_inhal_exhal_segments
    Auxiliary function for determination of the RIP sensor samples where inhalation and exhalation
    periods start and end.

Observations/Comments
---------------------
None

/\
"""

from os.path import exists as pathexist

import numpy
# import novainstrumentation as ni
from .process import smooth
from .visualise import plot, opensignals_kwargs, opensignals_color_pallet, opensignals_style
from .detect import detect_emg_activations
from .aux_functions import _generate_bokeh_file
from IPython.core.display import HTML
from bokeh.plotting import figure, show, save
from bokeh.models.annotations import Title
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import BoxAnnotation, Arrow, VeeHead
from .external_packages.novainstrumentation.freq_analysis import max_frequency, plotfft
from .external_packages.novainstrumentation.filter import bandpass
output_notebook(hide_banner=True)


def css_style_apply():
    """
    -----
    Brief
    -----
    Function that apply the css configurations to the Jupyter Notebook pages.

    -----------
    Description
    -----------
    Taking into consideration that, ultimately, biosignalsnotebooks Jupyter Notebooks are web pages,
    then a CSS file with the style options for customization of biosignalsnotebooks environment become
    particularly important.

    With CSS, the Jupyter Notebook template can be adapted in order to acquire the opensignals
    format, by changing background color, color pallet, font style...

    This function simply injects an HTML statement containing the style configurations.

    Returns
    -------
    out : IPython.core.display.HTML
        An IPython object that contains style information to be applied in the web page.

    """

    path = "styles/theme_style.css"
    if pathexist(path):
        style = open(path, "r").read()
    else:
        style = open("../../" + path, "r").read()

    print(".................... CSS Style Applied to Jupyter Notebook .........................")
    return HTML("<div id='style_import'>" + style + "</div>")


# /////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////// Plotting Auxiliary Functions //////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////

# =================================================================================================
# =================================== Acquire Category ============================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%% sampling_rate_and_aliasing.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_sample_rate_compare(data_dict, file_name=None):
    """
    -----
    Brief
    -----
    Is a plotting function that shows a sequence of ECG plots, demonstrating the relevance of
    choosing a wright sampling rate.

    -----------
    Description
    -----------
    Function intended to generate a Bokeh figure with Nx2 format, being N the number of keys of
    'data_dict' - one for each sampling rate (10, 100, 1000 Hz).

    At the first column is plotted a 10 seconds segment of the ECG signal at a specific
    sampling rate, while in the second column it will be presented a zoomed section of the ECG
    signal with 1 second, in order to the see the effect of choosing a specific sampling rate.

    Applied in the Notebook titled "Problems of a smaller sampling rate (aliasing)".

    ----------
    Parameters
    ----------
    data_dict : dict
        Dictionary that contains the data to be plotted
        ({"<sampling_rate_1>": {"time": <time_axis_1>, "data": <data_1>},
          "<sampling_rate_2>": {"time": <time_axis_2>, "data": <data_2>},
          ...})

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    """

    # Generation of the HTML file where the plot will be stored.
    file_name = _generate_bokeh_file(file_name)

    nbr_rows = len(list(data_dict.keys()))

    # List that store the figure handler.
    list_figures = plot([[]] * nbr_rows * 2, [[]] * nbr_rows * 2, y_axis_label="Raw Data",
                        x_axis_label="Time (s)", grid_lines=nbr_rows, grid_columns=2,
                        grid_plot=True, get_fig_list=True, show_plot=False)

    # Generation of Bokeh Figures.
    grid_list = []
    for iter, sample_rate in enumerate(list(data_dict.keys())):
        # List of figures in a valid gridplot format (each entry will define a row and each
        # subentry a column of the gridplot)
        grid_list += [[]]

        # Plotting of 10 seconds segment.
        # [Figure tile]
        title_unzoom = Title()
        title_unzoom.text = 'Sampling Rate: ' + sample_rate + " Hz"
        list_figures[2 * iter].title = title_unzoom

        # [Plot generation]
        list_figures[2 * iter].line(data_dict[sample_rate]["time"][:10 * int(sample_rate)],
                                    data_dict[sample_rate]["data"][:10 * int(sample_rate)],
                                    **opensignals_kwargs("line"))

        # Storage of customized figure.
        grid_list[-1] += [list_figures[2 * iter]]

        # Plotting of a zoomed section with 1 second.
        # [Figure tile]
        title_zoom = Title()
        title_zoom.text = 'Zoomed section @ ' + sample_rate + " Hz"
        list_figures[2 * iter + 1].title = title_zoom

        # [Plot generation]
        list_figures[2 * iter + 1].line(data_dict[sample_rate]["time"][:int(sample_rate)],
                                        data_dict[sample_rate]["data"][:int(sample_rate)],
                                        **opensignals_kwargs("line"))

        # Storage of customized figure.
        grid_list[-1] += [list_figures[2 * iter + 1]]

    # Organisation of figures in a gridplot.
    grid_plot_1 = gridplot(grid_list, **opensignals_kwargs("gridplot"))

    # Show representations.
    show(grid_plot_1)
    #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')

# [Old Version to be removed]
def acquire_subsamples_gp1(input_data, file_name=None):
    """
    Function invoked for plotting a grid-plot with 3x2 format, showing the differences in ECG
    signals accordingly to the chosen sampling frequency.

    Applied in the cell with tag "subsampling_grid_plot_1".

    ----------
    Parameters
    ----------
    input_data : dict
        Dictionary with ECG signal to present.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.
    """

    # Generation of the HTML file where the plot will be stored.
    file_name = _generate_bokeh_file(file_name)

    # Number of acquired samples (Original sample_rate = 4000 Hz)
    fs_orig = 4000
    nbr_samples_orig = len(input_data)
    data_interp = {"4000": {}}
    data_interp["4000"]["data"] = input_data
    data_interp["4000"]["time"] = numpy.linspace(0, nbr_samples_orig / fs_orig, nbr_samples_orig)

    # Constants
    time_orig = data_interp["4000"]["time"]
    data_orig = data_interp["4000"]["data"]

    # ============ Interpolation of data accordingly to the desired sampling frequency ============
    # sample_rate in [3000, 1000, 500, 200, 100] - Some of the available sample frequencies at Plux
    # acquisition systems
    # sample_rate in [50, 20] - Non-functional sampling frequencies (Not available at Plux devices
    # because of their limited application)
    for sample_rate in [3000, 1000, 500, 200, 100, 50, 20]:
        fs_str = str(sample_rate)
        nbr_samples_interp = int((nbr_samples_orig * sample_rate) / fs_orig)
        data_interp[fs_str] = {}
        data_interp[fs_str]["time"] = numpy.linspace(0, nbr_samples_orig / fs_orig,
                                                     nbr_samples_interp)
        data_interp[fs_str]["data"] = numpy.interp(data_interp[fs_str]["time"], time_orig,
                                                   data_orig)

    # List that store the figure handler.
    list_figures = []

    # Generation of Bokeh Figures.
    for iter_nbr, sample_rate in enumerate(["4000", "3000", "1000", "500", "200", "100"]):
        # If figure number is a multiple of 3 or if we are generating the first figure...
        if iter_nbr == 0 or iter_nbr % 2 == 0:
            list_figures.append([])

        # Plotting phase.
        list_figures[-1].append(figure(x_axis_label='Time (s)', y_axis_label='Raw Data',
                                       title="Sampling Frequency: " + sample_rate + " Hz",
                                       **opensignals_kwargs("figure")))
        list_figures[-1][-1].line(data_interp[sample_rate]["time"][:int(sample_rate)],
                                  data_interp[sample_rate]["data"][:int(sample_rate)],
                                  **opensignals_kwargs("line"))


# =================================================================================================
# ================================ Pre-Process Category ===========================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%% emg_fatigue_evaluation_median_freq.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_compare_act_config(signal, sample_rate, file_name=None):
    """
    -----
    Brief
    -----
    By invoking this function, a gridplot will be presented, in order to show the effect in muscular
    activation detection, when some input parameters of the algorithm are changed.

    -----------
    Description
    -----------
    It will be generated a Bokeh figure with 3x2 format, comparing the results of muscular
    activation algorithm when his input parameters are changed.

    At the first column are presented three plot zones, each plot zone is formed by an EMG signal,
    the smoothed signal and the muscular activation detection threshold.

    The smoothing level (SL) and threshold (TH) are customizable parameters, so, between these three
    figures, at least one of the parameters changed (each row of the gridplot shows graphical
    results obtained through the use of a specific set of algorithm parameter values [SL, TH] =
    [20, 10]% or [20, 50]% or [70, 10]%).

    At the second column is shown the result of applying muscular activation detection algorithm
    with the original EMG signal and a rectangular signal defining the start and end of each
    muscular activation period.

    Applied in the Notebook "Fatigue Evaluation - Evolution of Median Power Frequency".

    ----------
    Parameters
    ----------
    signal : list
        List with EMG signal to present.

    sample_rate : int
        Acquisitions sampling rate.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.
    """

    # Generation of the HTML file where the plot will be stored.
    file_name = _generate_bokeh_file(file_name)

    time = numpy.linspace(0, len(signal) / sample_rate, len(signal))[0:14000]
    signal = numpy.array(signal[0:14000]) - numpy.average(signal[0:14000])

    # Muscular Activation Detection.
    muscular_activation_begin_20_10, muscular_activation_end_20_10, smooth_signal_20_10, \
    threshold_level_20_10 = detect_emg_activations(list(signal), sample_rate, smooth_level=20,
                                                   threshold_level=10)
    threshold_level_20_10 = (numpy.max(signal) * threshold_level_20_10) / \
                            numpy.max(smooth_signal_20_10)
    smooth_signal_20_10 = (numpy.max(signal) * numpy.array(smooth_signal_20_10)) / \
                          numpy.max(smooth_signal_20_10)
    activation_20_10 = numpy.zeros(len(time))
    for activation in range(0, len(muscular_activation_begin_20_10)):
        activation_20_10[muscular_activation_begin_20_10[activation]:
                         muscular_activation_end_20_10[activation]] = numpy.max(signal)

    muscular_activation_begin_20_50, muscular_activation_end_20_50, smooth_signal_20_50, \
    threshold_level_20_50 = detect_emg_activations(list(signal), sample_rate, smooth_level=20,
                                                   threshold_level=50)
    threshold_level_20_50 = (numpy.max(signal) * threshold_level_20_50) / \
                            numpy.max(smooth_signal_20_50)
    smooth_signal_20_50 = (numpy.max(signal) * numpy.array(smooth_signal_20_50)) / \
                          numpy.max(smooth_signal_20_50)
    activation_20_50 = numpy.zeros(len(time))
    for activation in range(0, len(muscular_activation_begin_20_50)):
        activation_20_50[muscular_activation_begin_20_50[activation]:
                         muscular_activation_end_20_50[activation]] = numpy.max(signal)

    muscular_activation_begin_70_10, muscular_activation_end_70_10, smooth_signal_70_10, \
    threshold_level_70_10 = detect_emg_activations(list(signal), sample_rate, smooth_level=70,
                                                   threshold_level=10)
    threshold_level_70_10 = (numpy.max(signal) * threshold_level_70_10) / \
                            numpy.max(smooth_signal_70_10)
    smooth_signal_70_10 = (numpy.max(signal) * numpy.array(smooth_signal_70_10)) / \
                          numpy.max(smooth_signal_70_10)
    activation_70_10 = numpy.zeros(len(time))
    for activation in range(0, len(muscular_activation_begin_70_10)):
        activation_70_10[muscular_activation_begin_70_10[activation]:
                         muscular_activation_end_70_10[activation]] = numpy.max(signal)

    # Plotting of data in a 3x2 gridplot format.
    plot_list = plot([list([]), list([]), list([]), list([]), list([]), list([])],
                     [list([]), list([]), list([]), list([]), list([]), list([])],
                     grid_lines=3, grid_columns=2, grid_plot=True, get_fig_list=True,
                     show_plot=False)

    combination = ["Smooth Level: 20 %  Threshold Level: 10 %", "Smooth Level: 20 %  "
                                                                "Threshold Level: 50 %",
                   "Smooth Level: 70 %  Threshold Level: 10 %"]
    detect_dict = {"Smooth Level: 20 %  Threshold Level: 10 %": [smooth_signal_20_10,
                                                                 threshold_level_20_10,
                                                                 activation_20_10],
                   "Smooth Level: 20 %  Threshold Level: 50 %": [smooth_signal_20_50,
                                                                 threshold_level_20_50,
                                                                 activation_20_50],
                   "Smooth Level: 70 %  Threshold Level: 10 %": [smooth_signal_70_10,
                                                                 threshold_level_70_10,
                                                                 activation_70_10]}
    for plot_aux in range(0, len(plot_list)):
        title = Title()
        combination_temp = combination[int(plot_aux / 2)]
        plot_list[plot_aux].line(time, signal, **opensignals_kwargs("line"))
        if plot_aux % 2 == 0:
            title.text = combination_temp
            plot_list[plot_aux].line(time, detect_dict[combination_temp][0],
                                 **opensignals_kwargs("line"))
            plot_list[plot_aux].line(time, detect_dict[combination_temp][1],
                                 **opensignals_kwargs("line"))
            plot_list[plot_aux].yaxis.axis_label = "Raw Data"
        else:
            title.text = "Result for " + combination_temp
            plot_list[plot_aux].line(time, detect_dict[combination_temp][2],
                                 **opensignals_kwargs("line"))

        # x axis labels.
        if plot_aux in [4, 5]:
            plot_list[plot_aux].xaxis.axis_label = "Time (s)"

        plot_list[plot_aux].title = title

    grid_plot_ref = gridplot([[plot_list[0], plot_list[1]], [plot_list[2], plot_list[3]],
                              [plot_list[4], plot_list[5]]], **opensignals_kwargs("gridplot"))
    show(grid_plot_ref)
    #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')


def plot_median_freq_evol(time_signal, signal, time_median_freq, median_freq, activations_begin,
                          activations_end, sample_rate, file_name=None):
    """
    -----
    Brief
    -----
    Graphical representation of the EMG median power frequency evolution time series.

    -----------
    Description
    -----------
    Function intended to generate a Bokeh figure with 2x1 format, where each muscular activation
    period is identified through a colored box and the plot that shows the median frequency
    evolution is also presented.

    In the first cell is presented the EMG signal, highlighting each muscular activation.
    The second cell has the same time scale as the first one (the two plots are synchronized), being
    plotted the evolution time series of EMG median frequency.

    Per muscular activation period is extracted a Median Power Frequency value (sample), so, our
    window is a muscular activation period.

    Median power frequency is a commonly used parameter for evaluating muscular fatigue.
    It is widely accepted that this parameter decreases as fatigue sets in.

    Applied in the Notebook "Fatigue Evaluation - Evolution of Median Power Frequency".

    ----------
    Parameters
    ----------
    time_signal : list
        List with the time axis samples of EMG signal.

    signal : list
        List with EMG signal to present.

    time_median_freq : list
        List with the time axis samples of the median frequency evolution time-series.

    median_freq : list
        List with the Median Frequency samples.

    activations_begin : list
        List with the samples where each muscular activation period starts.

    activations_end : list
        List with the samples where each muscular activation period ends.

    sample_rate : int
        Sampling rate of acquisition.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.
    """

    # Generation of the HTML file where the plot will be stored.
    file_name = _generate_bokeh_file(file_name)

    list_figures_1 = plot([list(time_signal), list(time_median_freq)],
                          [list(signal), list(median_freq)],
                          title=["EMG Acquisition highlighting muscular activations",
                                 "Median Frequency Evolution"], grid_plot=True,
                          grid_lines=2, grid_columns=1, open_signals_style=True,
                          x_axis_label="Time (s)",
                          yAxisLabel=["Raw Data", "Median Frequency (Hz)"],
                          x_range=[0, 125], get_fig_list=True, show_plot=False)

    # Highlighting of each processing window
    for activation in range(0, len(activations_begin)):
        color = opensignals_color_pallet()
        box_annotation = BoxAnnotation(left=activations_begin[activation] / sample_rate,
                                       right=activations_end[activation] / sample_rate,
                                       fill_color=color, fill_alpha=0.1)
        box_annotation_copy = BoxAnnotation(left=activations_begin[activation] / sample_rate,
                                            right=activations_end[activation] / sample_rate,
                                            fill_color=color, fill_alpha=0.1)
        list_figures_1[0].add_layout(box_annotation)
        list_figures_1[1].add_layout(box_annotation_copy)

    gridplot_1 = gridplot([[list_figures_1[0]], [list_figures_1[1]]],
                          **opensignals_kwargs("gridplot"))
    show(gridplot_1)
    #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% digital_filtering.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_informational_band(freqs, power, signal, sr, band_begin, band_end,
                            legend="Signal Power Spectrum", x_lim=[], y_lim=[],
                            show_plot=False, file_name=None):
    """
    -----
    Brief
    -----
    With this function it is possible to present a plot containing the FFT Power Spectrum of an ECG
    signal, highlighting the informative frequency band.

    -----------
    Description
    -----------
    The FFT Power Spectrum, of an input signal, can be generated through plotfft function of
    novainstrumentation package (or periogram function of scipy package).
    The x axis (freqs) represents the frequency components of the signal, after decomposition was
    achieved by applying the Fourier Transform. The y axis (power) defines the relative weight of
    each frequency component (sinusoidal function) in the process of reconstructing the signal by
    re-summing of decomposition components.

    Additionally, it is also graphically presented a rectangular box showing which are the frequency
    components with relevant information for studying our input physiological signal.

    Note that each physiological signal has its own "informational band", whose limits should be
    specified in the input arguments "band_begin" and "band_end".

    Applied in the Notebook "Digital Filtering - A Fundamental Pre-Processing Step".

    ----------
    Parameters
    ----------
    freqs : list
        Frequency axis of power spectrum, defining which frequency components were used during the
        Fourier decomposition.

    power : list
        Power axis of power spectrum, defining the relative weight that each frequency component,
        inside "freqs", will have during the signal reconstruction.

    signal : list
        List containing the acquired signal samples.

    sr : int
        Sampling rate.

    band_begin : float
        Lower frequency inside the signal informational band.

    band_end : float
        Higher frequency inside the signal informational band.

    legend : str
        A string containing the legend that defines the power spectrum, for example: "ECG Power
        Spectrum".

    x_lim : list
        A list with length equal to 2, defining the first and last x value that should be presented.

    y_lim : list
        A list with length equal to 2, defining the first and last y value that should be presented.

    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    Returns
    -------
    out : bokeh figure
        Bokeh figure presenting the signal power spectrum and highlighting the informational band.
    """

    # Generation of the HTML file where the plot will be stored.
    file_name = _generate_bokeh_file(file_name)

    # ----------------------------- Verification procedure -----------------------------------------
    # Check if list is the type of input arguments x_lim and y_lim.
    if type(x_lim) is list and type(y_lim) is list:
        if len(x_lim) == 2 and len(y_lim) == 2:
            if len(x_lim) == 0:
                x_lim = [freqs[0], freqs[-1]]
            if len(y_lim) == 0:
                y_lim = [power[0], power[-1]]
        else:
            raise RuntimeError("The inputs arguments 'x_lim' and 'y_lim', when explicitly specified, "
                               "must be formed by two elements (defining the lower and upper limits "
                               "of the x and y axis).")
    else:
        raise RuntimeError("At least one of the input arguments (x_lim or y_lim) does not have a valid"
                           " type. The inputs must be lists.")

    # List that store the figure handler
    list_figures = []

    # Plotting of power spectrum
    list_figures.append(figure(x_axis_label='Frequency (Hz)', y_axis_label='Relative Weight',
                                 **opensignals_kwargs("figure"), x_range=(x_lim[0], x_lim[-1]),
                                 y_range=(y_lim[0], y_lim[1])))
    list_figures[-1].line(freqs, power, legend=legend,
                            **opensignals_kwargs("line"))

    # Highlighting of information band
    color = opensignals_color_pallet()
    box_annotation = BoxAnnotation(left=band_begin, right=band_end, fill_color=color,
                                   fill_alpha=0.1)
    list_figures[-1].circle([-100], [0], fill_color=color, fill_alpha=0.1,
                              legend="Informational Band")
    list_figures[-1].add_layout(box_annotation)

    # Determination of the maximum frequency
    max_freq = max_frequency(signal, sr)

    # Rejection band(above maximum frequency)
    color = "black"
    box_annotations = BoxAnnotation(left=max_freq, right=max_freq + 5, fill_color=color,
                                    fill_alpha=0.1)

    # Show of the plots with the rejection band
    list_figures[-1].circle([-100], [0], fill_color=color, fill_alpha=0.1, legend="Rejected Band")
    list_figures[-1].add_layout(box_annotations)
    list_figures[-1].add_layout(Arrow(end=VeeHead(size=15, line_color=color, fill_color=color,
                                                    fill_alpha=0.1), line_color=color,
                                        x_start=max_freq + 5, y_start=y_lim[1]/2,
                                        x_end=max_freq + 15, y_end=y_lim[1]/2))

    # Apply opensignals style.
    if len(numpy.shape(list_figures)) != 1:
        flat_list = [item for sublist in list_figures for item in sublist]
        opensignals_style(flat_list)
    else:
        opensignals_style(list_figures)

    # Present the generated plots.
    if show_plot is True:
        show(list_figures[-1])
        #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')

    return list_figures[-1]


def plot_before_after_filter(signal, sr, band_begin, band_end, order=1, x_lim=[], y_lim=[],
                             horizontal=True, show_plot=False, file_name=None):
    """
    -----
    Brief
    -----
    The use of the current function is very useful for comparing two power spectrum's (before and
    after filtering the signal).
    This function invokes "plot_informational_band" in order to get the power spectrum before
    applying the signal to the bandpass filter.

    -----------
    Description
    -----------
    The FFT Power Spectrum, of an input signal, can be generated through plotfft function of
    novainstrumentation package (or periogram function of scipy package).
    The x axis (freqs) represents the frequency components of the signal, after decomposition was
    achieved by applying the Fourier Transform. The y axis (power) defines the relative weight of
    each frequency component (sinusoidal function) in the process of reconstructing the signal by
    re-summing of decomposition components.

    It is presented a 1x2 gridplot for compaing the differences in frequency composition of the
    signal under analysis (before and after filtering).

    Additionally, it is also graphically presented a rectangular box showing which are the frequency
    components with relevant information for studying our input physiological signal.

    Applied in the Notebook "Digital Filtering - A Fundamental Pre-Processing Step".

    ----------
    Parameters
    ----------
    signal : list
        List containing the acquired signal samples.

    sr : int
        Sampling rate.

    band_begin : float
        Lower frequency inside the signal informational band.

    band_end : float
        Higher frequency inside the signal informational band.

    order : int
        Filter order.

    x_lim : list
        A list with length equal to 2, defining the first and last x value that should be presented.

    y_lim : list
        A list with length equal to 2, defining the first and last y value that should be presented.

    horizontal : bool
        If True then the generated figures will be joined together in an horizontal gridplot.
        When False the gridplot will be a vertical grid.

    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    Returns
    -------
    out : list
        List of Bokeh figures that compose the generated gridplot.
    """

    # Generation of the HTML file where the plot will be stored.
    file_name = _generate_bokeh_file(file_name)

    # Generation of FFT power spectrum accordingly to the filter order.
    for i in range(0, order + 1):
        # Initialisation and appending of data to the figures list.
        if i == 0:
            # Power spectrum
            freqs_after, power_after = plotfft(signal, sr)
            figure_after = plot_informational_band(freqs_after, power_after, signal, sr,
                                                   band_begin, band_end,
                                                   legend="Signal Power Spectrum", x_lim=x_lim,
                                                   y_lim=y_lim, show_plot=True)
            # List that store the figure handler
            list_figures = [[figure_after]]
        else:
            filter_signal = bandpass(signal, f1=band_begin, f2=band_end, order=i, fs=sr,
                                     use_filtfilt=True)

            # Power spectrum
            freqs_after, power_after = plotfft(filter_signal, sr)
            figure_after = plot_informational_band(freqs_after, power_after, filter_signal, sr,
                                                   band_begin, band_end,
                                                   legend="Filtered FFT (Order " + str(i) + ")",
                                                   x_lim=x_lim, y_lim=y_lim, show_plot=True)
            # Append data accordingly to the desired direction of representation.
            if horizontal is True:
                # Append to the figure list the power spectrum of the signal after filtering.
                list_figures[-1].append(figure_after)
            else:
                list_figures.append([figure_after])

    # Show gridplot.
    grid_plot_1 = gridplot(list_figures, **opensignals_kwargs("gridplot"))

    if show_plot is True:
        show(grid_plot_1)
        #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')

    return list_figures


def plot_low_pass_filter_response(show_plot=False, file_name=None):
    """
    -----
    Brief
    -----
    Taking into consideration the generic transfer function that defines the frequency response of
    a low-pass filter (|H|=1/(sqrt(1+(f/fc)^2n), where fc is the corner frequency and n is the
    filter order), the current function will generate a figure for comparing the frequency response
    accordingly to the filter order.

    -----------
    Description
    -----------
    In digital and analogical systems, a filter defines a system capable of attenuating specific
    frequency components of the signal that is applied to it.

    The filter behaviour can be mathematically defined through a transfer function, showing
    precisely the stop- and pass-bands.

    In the case of a low-pass filter, a structural parameter is the corner frequency (where the
    attenuation begins). Like the name suggests, all signal components with frequency below the
    corner frequency will be outputted without changes (they "pass" the filter), while components
    with frequency above the corner frequency suffers an attenuation (the bigger the difference
    between the frequency of the component and the corner frequency the bigger the attenuation).

    It is shown (in the same figure) the low-pass filter response for different order (1, 2, 3, 4,
    5, 6).

    Applied in the Notebook "Digital Filtering - A Fundamental Pre-Processing Step".

    ----------
    Parameters
    ----------
    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    Returns
    -------
    out : list
        List of Bokeh figures that compose the generated gridplot.
    """

    # Generation of the HTML file where the plot will be stored.
    file_name = _generate_bokeh_file(file_name)

    # Frequency list.
    freqs = numpy.linspace(1, 1200, 100000)
    cutoff_freq = 40

    # Generation of filter response.
    gain_functions = []
    legend_strs = []
    for order in range(1, 7):
        gain = 20*numpy.log10(1 / (numpy.sqrt(1 + (freqs / cutoff_freq)**(2*order))))

        # Storage of the determined gain values.
        gain_functions.append(gain)
        if order == 1:
            legend_strs.append("1st order filter")
        elif order == 2:
            legend_strs.append("2nd order filter")
        elif order == 3:
            legend_strs.append("3rd order filter")
        else:
            legend_strs.append(str(order) + "th order filter")


    # Generation of a Bokeh figure with the opensignals style.
    fig_list = plot([freqs / cutoff_freq]*len(gain_functions), gain_functions, legend=legend_strs,
                    title="Filter Response", x_axis_label="Normalized Frequency",
                    y_axis_label="Gain (dB)", x_axis_type="log", x_range=(0.1, 40),
                    y_range=(-120, 5), show_plot=True, get_fig_list=True)

    # Inclusion of a colored region showing the ideal behaviour.
    color=opensignals_color_pallet()
    box_annotation = BoxAnnotation(left=0.1, right=1, top=0, bottom=-120,
                                   fill_color=color,
                                   fill_alpha=0.3)
    fig_list[0].circle([-100], [0], fill_color=color, fill_alpha=0.3, legend="Ideal Filter Response")
    fig_list[0].add_layout(box_annotation)

    # Show figure.
    if show_plot is True:
        show(fig_list[0])
        #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')


# =================================================================================================
# =================================== Explain Category ============================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% respiration_slow.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# We stop here at 13h51m of 2nd October of 2018 :)
def plot_resp_slow(signal, rect_signal, sample_rate):
    """
    -----
    Brief
    -----
    Figure intended to represent the acquired RIP signal together with a rectangular signal defining
    inhalation and exhalation periods.

    -----------
    Description
    -----------
    Function design to generate a Bokeh figure containing the evolution of RIP signal, when
    slow respiration cycles occur, and the rectangular signal that defines the stages of
    inhalation and exhalation.

    Applied in the Notebook "Particularities of Inductive Respiration (RIP) Sensor ".

    ----------
    Parameters
    ----------
    signal : list
        List with the acquired RIP signal.

    rect_signal : list
        Data samples of the rectangular signal that identifies inhalation and exhalation
        segments.

    sample_rate : int
        Sampling rate of acquisition.
    """

    signal = numpy.array(signal) - numpy.average(signal)
    rect_signal = numpy.array(rect_signal)
    time = numpy.linspace(0, len(signal) / sample_rate, len(signal))

    # Inhalation and Exhalation time segments.
    # [Signal Binarisation]
    rect_signal_rev = rect_signal - numpy.average(rect_signal)
    inhal_segments = numpy.where(rect_signal_rev >= 0)[0]
    exhal_segments = numpy.where(rect_signal_rev < 0)[0]
    rect_signal_rev[inhal_segments] = numpy.max(rect_signal_rev)
    rect_signal_rev[exhal_segments] = numpy.min(rect_signal_rev)

    # [Signal Differentiation]
    diff_rect_signal = numpy.diff(rect_signal_rev)
    inhal_begin = numpy.where(diff_rect_signal > 0)[0]
    inhal_end = numpy.where(diff_rect_signal < 0)[0]
    exhal_begin = inhal_end
    exhal_end = inhal_begin[1:]

    # Generation of a Bokeh figure where data will be plotted.
    plot_aux = plot(list([0]), list([0]), showPlot=False)[0]

    # Edition of Bokeh figure (title, axes labels...)
    # [title]
    title = Title()
    title.text = "RIP Signal with slow cycles"
    plot_aux.title = title

    # [plot]
    plot_aux.line(time, signal, **opensignals_kwargs("line"))
    inhal_color = opensignals_color_pallet()
    exhal_color = opensignals_color_pallet()
    for inhal_exhal in range(0, len(inhal_begin)):
        if inhal_exhal == 0:
            legend = ["Inhalation", "Exhalation"]
        else:
            legend = [None, None]

        plot_aux.line(time[inhal_begin[inhal_exhal]:inhal_end[inhal_exhal]],
                  rect_signal_rev[inhal_begin[inhal_exhal]:inhal_end[inhal_exhal]],
                  line_width=2, line_color=inhal_color, legend=legend[0])

        if inhal_exhal != len(inhal_begin) - 1:
            plot_aux.line(time[exhal_begin[inhal_exhal]:exhal_end[inhal_exhal]],
                      rect_signal_rev[exhal_begin[inhal_exhal]:exhal_end[inhal_exhal]],
                      line_width=2, line_color=exhal_color, legend=legend[1])
        else:
            plot_aux.line(time[exhal_begin[inhal_exhal]:], rect_signal_rev[exhal_begin[inhal_exhal]:],
                      line_width=2, line_color=exhal_color, legend=legend[1])

    # [axes labels]
    plot_aux.xaxis.axis_label = "Time (s)"
    plot_aux.yaxis.axis_label = "Raw Data (without DC component)"

    show(plot_aux)



def plot_resp_diff(signal, rect_signal, sample_rate):
    """
    Function design to generate a Bokeh figure containing the evolution of RIP signal, when
    respiration was suspended for a long period, the rectangular signal that defines the
    stages of inhalation and exhalation and the first derivative of the RIP signal.

    Applied in the Notebook "Particularities of Inductive Respiration (RIP) Sensor ".

    ----------
    Parameters
    ----------
    signal : list
        List with the acquired RIP signal.

    rect_signal : list
        Data samples of the rectangular signal that identifies inhalation and exhalation
        segments.

    sample_rate : int
        Sampling rate of acquisition.
    """

    signal = numpy.array(signal) - numpy.average(signal)
    rect_signal = numpy.array(rect_signal)
    time = numpy.linspace(0, len(signal) / sample_rate, len(signal))
    signal_diff = numpy.diff(signal)

    # Inhalation and Exhalation time segments.
    # [Signal Binarization]
    rect_signal_rev = rect_signal - numpy.average(rect_signal)
    inhal_segments = numpy.where(rect_signal_rev >= 0)[0]
    exhal_segments = numpy.where(rect_signal_rev < 0)[0]
    rect_signal_rev[inhal_segments] = numpy.max(rect_signal_rev)
    rect_signal_rev[exhal_segments] = numpy.min(rect_signal_rev)

    # Normalized Data.
    norm_signal = signal / numpy.max(signal)
    norm_rect_signal = rect_signal_rev / numpy.max(rect_signal_rev)
    norm_signal_diff = signal_diff / numpy.max(signal_diff)

    # Smoothed Data.
    smooth_diff = smooth(signal_diff, int(sample_rate / 10))
    smooth_norm_diff = smooth(norm_signal_diff, int(sample_rate / 10))

    # Scaled Rectangular Signal.
    scaled_rect_signal = (rect_signal_rev * numpy.max(smooth_diff)) / numpy.max(rect_signal_rev)

    # [Signal Differentiation]
    diff_rect_signal = numpy.diff(rect_signal_rev)
    inhal_begin = numpy.where(diff_rect_signal > 0)[0]
    inhal_end = numpy.where(diff_rect_signal < 0)[0]
    exhal_begin = inhal_end
    exhal_end = inhal_begin[1:]

    # Generation of a Bokeh figure where data will be plotted.
    figure_list = plot([list([0]), list([0]), list([0])],
                                    [list([0]), list([0]), list([0])], gridPlot=True, gridLines=3,
                                    gridColumns=1, showPlot=False)

    # Edition of Bokeh figure (title, axes labels...)
    # [Top Figure]
    title = Title()
    title.text = "RIP Signal and Respiration Cycles"
    figure_list[0].title = title

    figure_list[0].line(time, signal, **opensignals_kwargs("line"))

    # [Plot of inhalation and exhalation segments]
    _inhal_exhal_segments(figure_list[0], list(time), list(rect_signal_rev), inhal_begin, inhal_end,
                          exhal_begin, exhal_end)
    figure_list[0].yaxis.axis_label = "Raw Data (without DC component)"

    # [Middle Figure]
    title = Title()
    title.text = "1st Derivative of RIP Signal and Respiration Cycles"
    figure_list[1].title = title

    figure_list[1].line(time[1:], smooth_diff, **opensignals_kwargs("line"))

    # [Plot of inhalation and exhalation segments]
    _inhal_exhal_segments(figure_list[1], list(time), list(scaled_rect_signal), inhal_begin,
                          inhal_end, exhal_begin, exhal_end)
    figure_list[1].yaxis.axis_label = "Raw Differential Data"

    # [Bottom Figure]
    title = Title()
    title.text = "RIP Signal and 1st Derivative (Normalized)"
    figure_list[2].title = title

    figure_list[2].line(time, norm_signal, **opensignals_kwargs("line"))
    figure_list[2].line(time[1:], smooth_norm_diff, **opensignals_kwargs("line"),
                        legend="RIP 1st Derivative")

    # [Plot of inhalation and exhalation segments]
    _inhal_exhal_segments(figure_list[2], list(time), list(norm_rect_signal), inhal_begin,
                          inhal_end, exhal_begin, exhal_end)
    figure_list[2].yaxis.axis_label = "Normalized Data"
    figure_list[2].xaxis.axis_label = "Time (s)"

    grid_plot_ref = gridplot([[figure_list[0]], [figure_list[1]], [figure_list[2]]],
                             **opensignals_kwargs("gridplot"))

    show(grid_plot_ref)


def _inhal_exhal_segments(fig, time, signal, inhal_begin, inhal_end, exhal_begin, exhal_end):
    """
    Auxiliary function used to plot each inhalation/exhalation segment.

    ----------
    Parameters
    ----------
    fig : Bokeh figure
        Figure where inhalation/exhalation segments will be plotted.

    time : list
        Time axis.

    signal : list
        Data samples of the acquired/processed signal.

    inhal_begin : list
        List with the indexes where inhalation segments begin.

    inhal_end : list
        List with the indexes where inhalation segments end.

    exhal_begin : list
        List with the indexes where exhalation segments begin.

    exhal_end : list
        List with the indexes where exhalation segments end.
    """

    inhal_color = opensignals_color_pallet()
    exhal_color = opensignals_color_pallet()
    for inhal_exhal in range(0, len(inhal_begin)):
        if inhal_exhal == 0:
            legend = ["Respiration Suspension", "Normal Breath"]
        else:
            legend = [None, None]

        fig.line(time[inhal_begin[inhal_exhal]:inhal_end[inhal_exhal]],
                 signal[inhal_begin[inhal_exhal]:inhal_end[inhal_exhal]], line_width=2,
                 line_color=inhal_color, legend=legend[0])

        if inhal_exhal != len(inhal_begin) - 1:
            fig.line(time[exhal_begin[inhal_exhal]:exhal_end[inhal_exhal]],
                     signal[exhal_begin[inhal_exhal]:exhal_end[inhal_exhal]], line_width=2,
                     line_color=exhal_color, legend=legend[1])
            if inhal_exhal == 0:
                fig.line(time[:inhal_begin[inhal_exhal]], signal[:inhal_begin[inhal_exhal]],
                         line_width=2, line_color=exhal_color, legend=legend[1])
        else:
            fig.line(time[exhal_begin[inhal_exhal]:], signal[exhal_begin[inhal_exhal]:],
                     line_width=2, line_color=exhal_color, legend=legend[1])


# 07/11/2018  00h02m :)
