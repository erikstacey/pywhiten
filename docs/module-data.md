# Data (Module)

The data module encapsulates several classes which are useful for storing and manipulating data for time series analysis.
Results of a frequency analysis are stored as objects of class Frequency, in a FrequencyContainer object. Lightcurve and Periodogram
classes provide the ability to store a time series and its pseudo-power spectrum.

## ```class Frequency```

A class which provides a complete description of a single-frequency variability model.

### Attributes

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

**Args:**

* ```float f``` | initial frequency
* ```float a``` | initial amplitude
* ```float p``` | initial phase
* ```float t0``` | Optional. Default 0. Reference time for phase
* ```function model_function = sin_model``` | A model function. This will typically be the model used to opimize the f, a, p parameters. This is required to fully specify the meaning of f, a, p, and t0. Must be of the form f(x, f, a, p). Defaults to sin model, as with anything else that utilizes a model of this form.
* ```n (int) = None``` | index label


**Returns:**

* ```None```

___

#### ```update(f : float, a : float, p : float)```

Updates f, a, and p parameters with the specified values.

**Args:**

* ```float f``` | New frequency
* ```float a``` | New amplitude
* ```float p``` | New phase

**Returns:**

* ```None```

___

#### ```get_parameters():```

Getter for the frequency, amplitude, and phase.

**Returns:**

* ```float``` current frequency
* ```float``` current amplitude
* ```float``` current phase

#### ```adjust_params()```

Adjusts the amplitude and phase parameters such that the amplitude is positive and the phase is within (0, 1) without affecting the model itself.

**Returns:**

* ```None```

___

#### ```evaluate_model(x:float)```

Evaluates the model at x and returns the value. If a numpy array is provided, an array of evaluated values is returned.

**Args:**

* ```float x``` | x value to evaluate model at.

**Returns:**

* ```float``` The value of the model at the specified x value.

___

#### ```prettyprint()```

Prints this frequency's parameters to console.

**Returns:**

* ```None```

___

## ```class FrequencyContainer```

A class which stores and operates on groups of ```Frequency``` objects. Generally used to hold a complex variability model consisting of several single-frequency variability components.

### Attributes

* ```list flist``` | A Python list containing ```Frequency``` objects.
* ```int n``` | The number of ```Frequency``` objects contained.

### Methods

#### ```__init__(*freqs:Frequency)```

Constructor which sets the initial flist to ```Frequency``` objects specified in the arbitrary number of positional arguments (```*freqs```).

#### ```get_flist()```

Getter for the list of frequencies.

**Returns:**

* ```list``` a list of ```Frequency``` objects

___

#### ```mf_model(time:Union[float, numpy.array], zp:float=0)```

Evaluates a summed model of all ```Frequency``` models contained at the value(s) specified in ```time```.

**Args:**

* ```time``` | either a float or an array specifying the values at which to evaluate the model
* ```float zp``` | A constant value to add to model.

**Returns:**

* Evaluated model. Same data type as the argument ```time```.

___

#### ```get_last_frequency()```

Returns the ```Frequency``` object which was added most recently.

**Returns:**

* ```Frequency``` | The last frequency in flist.

___

#### ```add_frequency(freq:Frequency)```

Adds a frequency to the list.

**Args:**

* ```Frequency freq``` | The frequency to add.

**Returns:**

* ```None```

___

#### ```compute_significances(residual_periodogram:Periodogram, eval: tuple)```

Computes significances for stored frequencies and stores them in class attributes for each frequency. Computes according to 3 methods and stores the results in separate class attributes by default.

**Args:**

* ```Periodogram residual_periodogram``` | A periodogram, assumed to consist of only noise, to use in evaluating the signal to noise ratios of each ```Frequency``` object model. Typically, when conducting pre-whitening, the analyzer removes all frequencies reasonably thought to be real and identifiable in the data then uses the residual periodogram to evaluate their confidence in their results.
* ```tuple eval``` | A tuple containing any or all of the strings ```"slf"```, ```"box"```, ```"poly"```, which specifies which methods to use when evaluating the significance.

**Returns:**

* ```None```

___

#### ```compute_parameter_uncertainties(residual_light_curve:Lightcurve```

Computes parameter uncertainties for the frequencies, amplitudes, and phases of each ```Frequency``` object contained using the modified Montgomery & O'donogue (1999) model.

**Args:**

* ```Lightcurve residual_light_curve``` | The residual light curve from the analysis, assumed to consist of only noise.

**Returns:**

* ```None```

___

## ```class Lightcurve```

A class which stores a set of time series data and provides methods for operating on it in a pre-whitening context.

### Attributes

* ```numpy.array time``` | The time axis of the time series.
* ```numpy.array data``` | The data axis of the time series.
* ```numpy.array err``` | Measurement weights on the values in ```data```. Commonly the measurement uncertainties, however can be arbitrary weights.
* ```Periodogram periodogram``` | A periodogram object storing the corresponding periodogram of the time series data.

### Methods

#### ```__init__(time:numpy.array, data:numpy.array, err:numpy.array = None)```

Constructor for the Lightcurve class. Sets attributes and builds a periodogram for the data.

**Args:**

* ```numpy.array time``` | Sets ```time```
* ```numpy.array data``` | Sets ```data```
* ```numpy.array err``` | Optional. Sets ```err```, otherwise ```err``` is ```None```
* ```dict cfg``` | Optional. Config dictionary passthrough to its child periodogram.

**Returns:**

* ```None```

___

#### ```unpack()```

Gets the time, data, and err arrays.

**Returns:**

* ```numpy.array``` | Time array
* ```numpy.array``` | Data array
* ```numpy.array``` | err array

___

#### ```measure_N_eff()```

Measures the number of sign changes in the light curve. Intended for use with differential light curves (and is not particularly useful otherwise).

**Returns:**

* ```int``` The number of sign changes.

___

#### ```std()```

Returns the standard deviation of the data axis of the light curve.

**Returns:**

* ```float``` | Standard deviation of the light curve

___

#### ```t_span()```

Returns the difference between the maximum and minimum time value - the time span of the light curve.

**Returns:**

* ```float``` | Time span of light curve

___

#### ```debug_plot()```

Plots the light curve and shows it in a rudimentary plot. Intended for debugging.

**Returns:**

* ```None```

___

## Periodogram

A class storing a Lomb-Scargle periodogram.

### Attributes

* ```numpy.array lsfreq``` | The frequency axis of the LS periodogram.
* ```numpy.array lsamp``` | The amplitude axis of the LS periodogram.
* ```list log_polypar``` | Optimized parameters of a low-order polynomial fit to the log-log periodogram. These must be used to evaluate models in log-log space.
* ```list slf_p``` | Optimized parameters of an SLF variability fit to the periodogram. Formatted as ```[x0, alpha_0, gamma, Cw]```.
* ```list sl_p_err``` | Uncertainties on the optimized parameters stored in slf_p.
* ```float p_approx_nyquist_f``` | The nyquist frequency assuming even sampling in the time series data. This will NOT be the nyquist frequency for data with gaps, but it is used to automatically generate periodogram boundaries anyways.
* ```p_resolution``` | The minimum separation necessary to resolve two periodic components close in frequency usng a Lomb-Scargle based pre-whitening methodology using the provided light curve.
* ```cfg``` | A configuration dictionary. See [here](https://pywhiten.readthedocs.io/en/latest/configuration/) for more information.

### Methods

#### ```__init__(time:numpy.array, data:numpy.array, lsfreq: Union[str, numpy.array], fbounds : tuple, pts_per_res : int, cfg:dict)```

Constructor for the periodogram. Takes the light curve and some parameters, and computes an appropriate amplitude-spectrum periodogram.

**Args:**

* ```numpy.array time``` | Time series time axis
* ```numpy.array data``` | Time series data axis
* ```Union[str, np.array] lsfreq``` | Optional. An array holding a frequency grid to use as the periodogram frequency axis. If set to ```"auto"```, automatically determines a frequency grid. Default: ```"auto"```
* ```tuple fbounds``` | Optional. Only used if lsfreq is set to ```"auto"```. A 2-tuple containing an upper and lower bound used to set the boundaries over which to compute the grid.
* ```int pts_per_res``` | Optional. Only used if lsfreq is set to ```"auto"```. The number of discrete points to place in the frequency grid per resolution element. The resolution element is taken to be 1.5/deltaT, where deltaT is the time baseline of the light curve.
* ```dict cfg``` | Optional. Allows the configuration dictionary to be specified directly.

___

#### ```highest_ampl(excl_mask: np.array)```

Selects the highest peak in the periodogram, and returns its frequency and amplitude.

**Args:**

* ```numpy.array excl_mask```: A boolean mask of the same length of lsfreq and lsamp, which is used to exclude points from selection. If the mask value is True, it can be selected. Otherwise, it cannot.

**Returns:**

* ```float``` | Frequency value of the highest peak
* ```float``` | Amplitude value of the highest peak

___

#### ```find_troughs(center:float)```

Finds the indices corresponding to local minima on either side of the specified value.

**Args:**

* ```float center``` | A center value in frequency to search around

**Returns:**

* ```int``` | The index of the leftward local minimum
* ```int``` | The index of the rightward local minimum

___

#### ```find_index_of_freq(t:float)```

Finds the index of lsfreq holding the closest frequency to ```t```.

**Args:**

* ```float t``` | A frequency to search for

**Returns:**

* ```int``` | The index of the closest value in lsfreq

___

#### ```peak_sig_box(center_val_freq : float, freq_amp : float, bin_r : float)```

Gets the significance of a peak by considering the average periodogram value around the peak. Should NOT be used to measure significance in a residual periodogram where the peak has already been extracted (use sig_box() instead)

**Args:**

* ```float center_val_freq``` | Peak frequency value
* ```float freq_amp``` | Peak amplitude value
* ```float bin_r``` | The radius around which to search, in equivalent units to lsfreq.

**Returns:**

* ```float``` | The evaluated significance

**Raises**:

* ```AverageRadiusTooNarrow``` | The average radius is less than the radius of the peak itself. As this function finds the edges of the peak and excludes values within the peak from the box average, this leads to averaging an empty list.

___

#### ```sig_box(center_val_freq : float, freq_amp : float, bin_r : float)```

Find the significance of a periodic component model by comparing its amplitude against the average residual
periodogram near its frequency.

**Args:**

* ```float center_val_freq``` | Model frequency value
* ```float freq_amp``` | Model amplitude value
* ```float bin_r``` | The radius around which to search, in equivalent units to lsfreq.

**Returns:**

* ```float``` | The evaluated significance for the periodic model

___

#### ```fit_lopoly(poly_order : int)```

Fits the periodogram with a polynomial in log-log space and stores the coefficients in the attribute log_polypar.

**Args:**

* ```int poly_order``` | The order of polynomial to fit

**Returns:**

* ```None```

___

#### ```sig_poly(center_val_freq:float, freq_amp:float)```

Finds the significance of a periodic component model by performing a low-order polynomial fit in log-log space.

**Args:**

* ```float center_val_freq``` | Model frequency value
* ```float freq_amp``` | Model amplitude value

**Returns:**

* ```float``` | The evaluated significance for the periodic model

___

#### ```fit_slf()```

Fits the periodogram with a stochastic low-frequency variability model, and stores the paramters in ```slf_p```. Also populates ```slf_p_err``` with parameter uncertainties.

**Returns:**

* ```None```

___

#### ```sig_slf(center_val_freq:float, freq_amp:float)```

Finds the significance of a periodic component model by comparing its amplitude against an SLF noise fit.

**Args:**

* ```float center_val_freq``` | Model frequency value
* ```float freq_amp``` | Model amplitude value

**Returns:**

* ```float``` | The evaluated significance for the periodic model

___

#### ```select_peak(method : str, min_prov_sig : float, mask : np.array)```

Determines a frequency-amplitude pair from the periodogram. This can be achieved through a few different methods, the simplest is when ```method="highest"```, which simply selects the highest value in amplitude from the periodogram and returns it along with its frequency. This function is used to select candidate frequency/amplitude pairs for pre-whitening.

**Args:**

* ```string method``` | Must be one of ```["highest", "slf", "poly"]```, which sets which of the sig_x functions to use to evaluate the provisional significance of candidate peaks. Note: ```"poly"``` is untested in the current version, and likely to be deprecated if this package is further developed in the future. ```"highest"``` ignores the provisional significance criterion and simple selects the highest amplitude in the periodogram.
* ```float min_prov_sig``` | The minimum provisional significance criterion to accept a candidate frequency-amplitude pair. If ```method``` is ```"slf"``` or ```"poly"```, a noise model is computed for the entire periodogram and then lsamp values below the noise model multiplied by ```min_prov_sig``` are indicated in a boolean mask. That mask is then used as an exclusion mask when selecting the highest peak by amplitude.
* ```numpy.array``` | A boolean mask used to exclude periodogram points from selection.

**Returns:**

* ```float``` | The peak frequency. ```None``` if no peak could be identified.
* ```float``` | The peak amplitude. ```None``` if no peak could be identified.

___

#### ```eval_slf_model(x: float)```

Performs an SLF fit if one hasn't been performed already, and evaluates the SLF model at the x value provided.

**Args:**

* ```float x```

**Returns:**

* ```float``` | SLF model evaluated at ```x```

___
