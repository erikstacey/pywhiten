"""
pywhiten is a python package for conducting Lomb-Scargle-based pre-whitening to identify
frequencies, amplitudes, and phases of sinusoidal variability signals in time series data. The core functionality of
this program was written and validated by Erik William Stacey as a principle component of the analysis presented in
his research thesis for his Master of Science at the Royal Military College of Canada.
"""

from pywhiten.PyWhitener import PyWhitener
import pywhiten.data
import pywhiten.pwio
import pywhiten.optimization
