# Optimization (Module)

This module stores classes and functions which are used for performing mathematical optimizations, a critical component of a Lomb-Scargle-based pre-whitening routine.

## models

```pywhiten.optimization.models``` stores all the functions used for optimizations. These are listed below.

* ```chisq(data:numpy.array, model:numpy.array, err:numpy.array)->float``` | Returns the chi squared of the provided model.
* ```sin_model(x:numpy.array, f:float, a:float, p:float) -> numpy.array ``` | A sinusoidal model of the form ```f(x) = a*sin(2*pi*(fx+p))```
* ```cos_model(x:numpy.array, f:float, a:float, p:float) -> numpy.array ``` | A (co-)sinusoidal model of the form ```f(x) = a*cos(2*pi*(fx+p))```
* ```n_sin_model(x:numpy.array, *params:float) -> numpy.array``` | A model consisting of n superimposed sinusoidal models from ```sin_model```. ```*params``` must be of the form: ```*frequencies, *amplitudes, *phases, zero point```, and therefore will be of length ```3n+1```.

* ```n_cos_model(x:numpy.array, *params:float) -> numpy.array``` | A model consisting of n superimposed sinusoidal models from ```cos_model```. ```*params``` must be of the form: ```*frequencies, *amplitudes, *phases, zero point```, and therefore will be of length ```3n+1```.

* ```n_model_poly(x:np.array, *params:float) -> np.array``` | A polynomial model of order ```n```. ```*params``` must contain the polynomial coefficients and must of length ```n+1```. The model is evaluated as ```f(x) = params[0] + x * params[1] + x^2 * params[2] ... x^n * params[n]```.

* ```slf_noise(x:np.array, *params) -> np.array``` | The Bowman et al. (2019) SLF variability model. ```*params``` must be of the form ```[x0, alpha_0, gamma, Cw]```.

## ```class Optimizer```

A class which handles chi-squared minimization of single-frequency and multi-frequency sinusoidal models.

### Attributes:

* ```function sf_func``` | A sinusoidal function taking arguments of the format ```f(x:numpy.array, f:float, a:float, p:float)``` used for single-frequency optimizations and summed for multi-frequency optimizations (when using LMFit as the optimization engine, which is the only option at present).

* ```function mf_func``` | A function taking arguments of the format x:ndarray, *pars, where *pars is an arbitrarily large set of floats arranged such that it contains a group of frequency guesses followed by a group of amplitude guesses followed by a group of phase guesses followed by a guess for the zero point. The frequency, amplitude, and phase guesses must be of equal size, meaning *pars should be of length 3n+1 where n is some positive integer. Not currently used for optimization, but left in case the scipy option for minimization is re-implemented.
* ```dict cfg``` | A configuration dictionary.
* ```c_zp``` | The zero point value of the last fit performed with this object.

### Methods

#### ```__init__(cfg : dict) ```

Constructor for this object. Requires a configuration dictionary, and sets up the fitting functions.

**Args:**

* ```dict cfg``` | A configuration dictionary.

___

#### ```single_frequency_optimization(x: numpy.array, data: numpy.array, err: numpy.array, f0: float, a0: float, p0: float)```

Determines optimized parameters for a fit of a sinusoidal model to an x-y dataset.

**Args:**

* ```numpy.array x``` | x-axis of data to be fit
* ```numpy.array data``` | y-axis of data to be fit
* ```numpy.array err``` | y-axis weights of data to be fit
* ```float f0``` | An initial guess for the model frequency
* ```float a0``` | An initial guess for the model amplitude
* ```float p0``` | An initial guess for the model phase

**Returns:**

* ```float``` | The optimized model frequency
* ```float``` | The optimized model amplitude
* ```float``` | The optimized model phase
* ```numpy.array``` | The optimized single-frequency model evaluated at all values of ```x```

___

#### ```multi_frequency_optimization(x: numpy.array, data: numpy.array, err: numpy.array, freqs: list)```

Determines the optimized parameters for a fit of a composite sinusoidal model to an x-y dataset, and updates parameters in place. Sets the ```c_zp``` attribute to the optimized value when the fit is complete as well.

**Args:**

* ```numpy.array x``` | x-axis of data to be fit
* ```numpy.array data``` | y-axis of data to be fit
* ```numpy.array err``` | y-axis weights of data to be fit
* ```list freqs``` | A list of ```pywhiten.data.Frequency``` objects. The values of ```f```, ```a```, and ```p``` for these objects are used as the initial guesses for the fit. When the optimization is complete, the ```Frequency``` object parameters are updated in-place.

**Returns:**

* ```numpy.array``` | The optimized multi-frequency model evaluated at all values of ```x```

___