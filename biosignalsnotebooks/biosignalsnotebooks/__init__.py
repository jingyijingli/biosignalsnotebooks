"""
OPENSIGNALSFACTORY PACKAGE INITIALISATION FILE (WITH IMPORT STATEMENTS)

The main purpose of biosignalsnotebooks package is to support the users of PLUX acquisition
devices, such as biosgnalsplux or bitalino, in some processing tasks that can be applied to the
acquired electrophysiological signals, namely ECG, EMG...

This package had been developed as part of the "OpenSignals Tools" project, that offers a set of
Jupyter Notebooks (tutorials) where it is explained step by step how the user can execute the
previously mentioned processing tasks (such as detection of muscular activation from EMG signal,
determination of each cardiac cycle duration from an ECG acquisition or monitoring fatigue by
generating EMG median power frequency evolution time series).

At the end of each Notebook is referred the correspondent biosignalsnotebooks function that synthesises
the processing functionality presented step by step.

In spite of being 'part' of an integrate solution for OpenSignals users, this package can be used
independently.

Package Documentation
---------------------
The docstring presented as the initial statement of each module function will help the user to
correctly and effectively use all biosignalsnotebooks functions.

A full guide that collects all the function docstring is available for download at:
...

OpenSignals Tools Project Repository
------------------------------------
More information's about the project and the respective files are available at:

https://github.com/biosignalsplux/biosignalsnotebooks

Available Modules
-----------------
aux_functions
    Includes a set of auxiliary functions that are invoked in other biosignalsnotebooks modules.
    This module has a 'private' classification, i.e., it was not specially designed for users.
__notebook_support__
    Set of functions invoked in OpenSignals Tools Notebooks to present some graphical results.
    These function are only designed for a single end, but we made them available to the user if he
    want to explore graphical functionalities in an example format.
conversion
    Module responsible for the definition of functions that convert Raw units (available in the
    acquisition files returned by OpenSignals) and sample units to physical units like mV, A, ºC,
    s,..., accordingly to the sensor under analysis.
detect
    Contains functions intended to detect events on electrophysiological signals.
extract
    Ensures to the user that he can extract multiple parameters from a specific electrophysiological
    signal at once.
open
    Module dedicated to read/load data from .txt and .h5 files generated by OpenSignals.
    With the available functions the user can easily access data inside files (signal samples)
    together with the metadata in the file header.
process
    Processing capabilities that are more general than the categories of the remaining modules.
signal_samples
    A module that gives an easy access to the biosignalsnotebooks dataset/library of signals (used in
    OpenSignals Tools Notebooks).
visualise
    Graphical data representation functions based on the application of Bokeh main functionalities.

/\
"""

from .conversion import *
from .detect import *
from .extract import *
from .load import *
from .process import *
from .visualise import *
from .signal_samples import *
from .factory import *
from .synchronisation import *
from .train_and_classify import *
from .__notebook_support__ import *
from .synchronisation import *
from .android import *

# 11/10/2018 16h45m :)
