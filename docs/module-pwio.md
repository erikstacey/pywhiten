# pwio (Module)

This module contains functions and classes for handling input and output for pywhiten.

## pywhiten.pwio.utilities

Some utility functions are contained here:

* ```flux2mag(data:numpy.array, ref_flux:float, ref_mag:float) -> numpy.array``` | Converts an array of flux values ```data``` to an array of magnitude values, using a reference flux ```ref_flux``` and corresponding magnitude ```ref_mag```.

*```flux2mag_e(data:numpy.array, ref_flux:float, ref_mag: float, err: numpy.array) -> numpy.array, numpy.array``` | Same as ```flux2mag```, however takes an additional argument ```err``` which contains uncertainties on ```data```, and returns an additional array with uncertainties in magnitude.

*```format_output(n: float, e: float, npts: int) -> string``` | Taking a nominal measurement ```n``` and its error ```e```, converts it to a string expressing the measurement of the form ```1.23(1)```. ```npts``` indicates the number of digits of the uncertainty to retain (e.g. ```npts=2``` -> ```1.234(12)```).

## OutputManager

This class handles saving plots and data for the pre-whitening process.

### Attributes

* ```function sf_func``` | The function used to model single-frequency sinusoidal models
* ```function mf_func``` | The function used to model multi-frequency sinusoidal models. Unused, but kept for now in case SciPy functionality is re-implemented.

* ```dict output_dirs``` | A dictionary mapping strings to strings storing the output folder structure. Inadvisable to modify this.

### Methods

#### ```__init__(cfg)```

Constructor. Responsible for cleaning out the output directory if specified in the config as well as making the directory structure. **THIS WILL DELETE EVERYTHING IN THE OUTPUT DIRECTORY SPECIFIED IN CFG IF ```clean_dirs``` IS SET IN CFG WHEN THIS OBJECT IS INITIALIZED.**

**Args:**

* ```dict cfg``` | A configuration dictionary.

___

#### ```save_it(lcs: list, frequency_container: FrequencyContainer, zp: float)```

Saves the results from a single iteration. This is intended to be called at each iteration, passing in the complete light curve list and frequency container. Saves light curve and periodogram data, and plots/saves light curves, periodograms, and models. Only operates on the most recent item of each, however requires the full results for e.g. multi-frequency models.

**Args:**

* ```list lcs``` | A list of ```Lightcurve``` objects where each subsequent lightcurve in the list is from a subsequent iteration in a pre-whitening analysis
* ```FrequencyContainer frequency_container``` | A FrequencyContainer object which stores the results from the pre-whitening analysis corresponding to the sequence of lightcurves in ```lcs```.
* ```float zp``` | Optional. The constant zero point of the complete variability model.

**Returns:**

* ```None```

___

#### ```get_freq_params_in_mmag(freq:Frequency)```
Get the amplitude in mmag for a frequency with its amplitude measured in flux, and the appropriately-adjusted phase. The conversion to magnitude flips the shape of the variability component described by the freq object, therefore this multiplies the amplitude in magnitude by -1 and adjusts the phase appropriately.

**Args:**

* ```Frequency freq``` | The frequency which holds the parameters to convert

**Returns:**

* ```float``` | The amplitude in mmag
* ```float``` | The amplitude uncertainty in mmag
* ```float``` | The adjusted phase phase
* ```float``` | The converted initial amplitude in mmag

___

#### ```save_freqs(freqs:FrequencyContainer)```
Formats and saves all the frequencies contained in a FrequencyContainer as a csv under the base output directory as ```"frequencies.csv"```.

**Args:**

* ```FrequencyContainer freqs``` | A ```FrequencyContainer``` object containing ```Frequency``` objects to be saved.

**Returns:**

* ```None```

___

#### ```save_freqs_as_latex_table(freqs:FrequencyContainer)```
Formats and saves all the frequencies contained in a FrequencyContainer as a formatted LaTeX table under the auxiliary output directory as ```"frequencies.csv"```.

**Args:**

* ```FrequencyContainer freqs``` | A ```FrequencyContainer``` object containing ```Frequency``` objects to be saved.

**Returns:**

* ```None```

___

#### ```save_lc(lightcurve: Lightcurve, path:string)```
Saves a lightcurve object at the specified path as a space-delimited 3-column file of format ```[time, data, err]```.

**Args:**

* ```Lightcurve lightcurve``` | The lightcurve to save
* ```string path``` | The path to save the file at

**Returns:**

* ```None```

___

#### ```save_pg(periodogram: Periodogram, path:string)```
Saves a periodogram object at the specified path as a space-delimited 2-column file of format ```[lsfreq, lsamp]```.

**Args:**

* ```Periodogram periodogram``` | The lightcurve to save
* ```string path``` | The path to save the file at

**Returns:**

* ```None```

___





