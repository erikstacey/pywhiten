"""
pywhiten is a python package for conducting Lomb-Scargle-based pre-whitening to identify
frequencies, amplitudes, and phases of sinusoidal variability signals in time series data.

The basic methodology implemented in this frequency analysis package is based on least-squares fitting of sinusoidal
models to time series data (based on the seminal papers of N. R. Lomb (1976) and J. D. Scargle (1982). This is a
popular approach to frequency analysis within the observational astronomy community, however other approaches have seen
a significant degree of use (e.g. Phase Dispersion Minimization) as well. The approach implemented in this package has
the advantages of 1) being computationally fast, utilizing the Lomb-Scargle Periodogram and Levenberg-Marquardt
minimization routines, and 2) providing results in an easily-quantifiable form. The core functionality of this program
was written and validated by Erik William Stacey as a principle component of the analysis presented in his MSc
thesis at the Royal Military College of Canada.

Classes:
    Pywhitener
Modules:
    data: Contains data structures that are useful for pre-whitening
    optimization: Contains all mathematical optimization functionality for the package
    pwio: Contains input/output functionality
Variables:
    default_cfg (dict): A dictionary storing the default configuration
    pkg_path (string): A string storing the local path to the package
"""
import pywhiten.cfg
import pywhiten.data
import pywhiten.pwio
import pywhiten.optimization
from pywhiten.PyWhitener import PyWhitener









