# Data (Module)

The data module encapsulates several classes which are useful for storing and manipulating data for time series analysis.
Results of a frequency analysis are stored as objects of class Frequency, in a FrequencyContainer object. Lightcurve and Periodogram
classes provide the ability to store a time series and its pseudo-power spectrum.

## Frequency
An object a complete description of a single-frequency variability model.
### Attributes:
* ```float f``` | Frequency parameter. 
* ```float a``` | Amplitude parameter.
* ```float p``` | Phase parameter.
* ```float f0``` | Frequency parameter when the object was initialized.
* ```float a0``` | Amplitude parameter when the object was initialized.
* ```float p0``` | Phase parameter when the object was initialized.
* ```float sigma_f``` | Uncertainty on frequency.
* ```float sigma_a``` | Uncertainty on amplitude.
* ```float sigma_p``` | Uncertainty on phase.
* ```float t0``` | The reference time for the model. A measurement of phase is meaningless without a reference time. At the time t0, the model will be at phase p.
* ```float sig_poly``` | The statistical significance of this model measured using a low-order polynomial fit to the residual periodogram in log-log space. Defaults to 0.
* ```float sig_avg``` | The statistical significance of this model measured using a box-average of the residual periodogram. Defaults to 0.
* ```float sig_slf``` | The statistical significance of this model measured using a fit of stochastic low-frequency variability. Defaults to 0.
* ```int n``` | An index label for the model. Typically this will be used to identify models during pre-whitening, with the first model assigned n=0 and subsequent models assigned incremental integers.
* ```function model_function``` | Model function of form f(x, f, a, p) which is used to describe the model in tandem with the f, a, and p attributes. Constructor will set this to a sinusoidal model f(x) = Asin(2pi*(fx+p)) by default.

### Methods
#### ```__init__(f:float, a:float, p:float, t0:float, model_function : function = sin_model n: Union[int, None]=None)```
Constructor. Sets initial values for attributes.

Args:
* ```float f``` | initial frequency
* ```float a``` | initial amplitude
* ```float p``` | initial phase
* ```float t0``` | reference time for phase
* ```function model_function = sin_model``` | A model function. This will typically be the model used to opimize the f, a, p parameters. This is required to fully specify the meaning of f, a, p, and t0. Must be of the form f(x, f, a, p). Defaults to sin model, as with anything else that utilizes a model of this form.
* ```n (int) = None``` | index label


Returns:
* ```None```

#### ```update(f : float, a : float, p : float)```
Updates f, a, and p parameters with the specified values.
* ```float f``` | New frequency
* ```float a``` | New amplitude
* ```float p``` | New phase

Returns:
* ```None```

#### ```get_parameters():```
Getter for the frequency, amplitude, and phase.
Returns:
* ```float``` current frequency
* ```float``` current amplitude
* ```float``` current phase

#### ```adjust_params()```
Adjusts the amplitude and phase parameters such that the amplitude is positive and the phase is within (0, 1) without affecting the model itself.
Returns:
* ```None```

#### ```evaluate_model(x:float)```
Evaluates the model at x and returns the value. If a numpy array is provided, an array of evaluated values is returned.

Returns:
* ```float``` The value of the model at the specified x value.

#### ```prettyprint()```
Prints this frequency's parameters to console.

Returns:
* ```None```


