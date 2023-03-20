"""
A module for handling pre-whitening input and output

This includes some utility functions for converting between flux and magnitude as well as a function for formatting
output measurements with uncertainties in the common 1.23(1) format. The OutputManager class provides functionality for
setting up an output structure, making consistent lightcurve and periodogram plots, and saving output and auxiliary
data
Classes:
    OutputManager

Functions:
    flux2mag
    flux2mag_e
    format_output
"""

from pywhiten.pwio.OutputManager import OutputManager
from pywhiten.pwio.utilities import *