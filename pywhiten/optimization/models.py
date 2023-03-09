"""
Models used for chi-squared minimization by the Optimizer are defined here.
"""

import numpy as np

def chisq(data, model, err):
    """Measures chi squared for a model array given a data array and weights"""
    return sum(((data-model)/err)**2)

def sin_model(x, f, a, p):
    """Basic sinusoidal model"""
    return a*np.sin(2*np.pi*(f*x+p))

def cos_model(x, f, a, p):
    """Basic (co)sinusoidal model"""
    return a*np.cos(2*np.pi*(f*x+p))

def n_sin_model(x, *params):
    """Sums an arbitrary number of basic sinusoidal models. Number of sinusoids is defined by the number of parameters
    provided, and the *params input should follow the following form: *freqs, *amps, *phases, zp(=zero point)"""
    l = len(params)-1
    nfreqs = len(params)//3
    y = np.zeros(len(x))
    for i in range(l // 3):
        y += sin_model(x, params[i], params[i+nfreqs], params[i+2*nfreqs])
    return y + params[-1]

def n_cos_model(x, *params):
    """Sums an arbitrary number of basic sinusoidal models. Number of sinusoids is defined by the number of parameters
    provided, and the *params input should follow the following form: *freqs, *amps, *phases, zp(=zero point)"""
    l = len(params)-1
    nfreqs = len(params)//3
    y = np.zeros(len(x))
    for i in range(l // 3):
        y += cos_model(x, params[i], params[i+nfreqs], params[i+2*nfreqs])
    return y + params[-1]

def n_model_poly(x, *params):
    """A polynomial model of arbitrary order, determined by the number of input parameters"""
    power = 0
    try:
        out = np.zeros(len(x))
    except TypeError:
        out = 0
    for p in params:
        out += p * (x**power)
        power += 1
    return out

def slf_noise(x, *params):
    """The model presented in Bowman et al. (2019) describing stochastic low-frequency variability in massive stars"""
    # params = [x0, alpha_0, gamma, Cw]
    return params[1] / (1 + (x / params[0]) ** params[2]) + params[3]