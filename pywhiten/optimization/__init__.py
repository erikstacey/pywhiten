"""
Handles the relevant optimization for pre-whitening, including fitting sinusoidal single-frequency and multi-frequency
models.

Typical usage is to use the Optimizer object to conduct single-frequency and multi-frequency optimizations at each
iteration of pre-whitening. This is useful as it handles correctly setting up Frequency objects which are returned,
and retains some information between iterations (e.g. the floating zero point parameter). Sinusoidal and periodogram
noise models can also be directly accessed through this module.
Classes:
    Optimizer
Functions:
    chisq
    sin_model
    cos_model
    n_sin_model
    n_cos_model
    n_model_poly
    slf_noise
"""

from pywhiten.optimization.Optimizer import Optimizer
from pywhiten.optimization.models import *
