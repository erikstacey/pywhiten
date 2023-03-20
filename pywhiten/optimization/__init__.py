"""
Handles the relevant optimization for pre-whitening, including fitting sinusoidal single-frequency and multi-frequency
models.
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
