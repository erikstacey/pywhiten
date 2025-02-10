# Pywhitener

The ```Pywhitener``` object is the heart of the pywhiten package, and provides the automated instance-based frequency analysis functionality to the package. For some examples and guidance on how to apply pywhitener objects, please refer to the [getting started guide](https://pywhiten.readthedocs.io/en/latest/getting-started/).

## ```class Pywhitener```
### Attributes
* ```list lcs``` | A list of ```Lightcurve``` objects, which holds the initial light curve and the residual light curves generated during the pre-whitening process
* ```FrequencyContainer freqs``` | A ```FrequencyContainer``` object holding the single-frequency variability models, in ```Frequency``` objects, constituting the complete variability model
* ```dict cfg``` | A configuration dictionary. See https://pywhiten.readthedocs.io/en/latest/configuration/
* ```OutputManager output_manager``` | The output manager responsible for handling saving data and plots during the pre-whitening
* ```Optimizer optimizer``` | The optimizer object responsible for handling single-frequency and multi-frequency optimization steps

### Methods

#### ```__init__(time: numpy.array, data: numpy.array, err: numpy.array, cfg_file: string, cfg: dict)```
Sets up the pywhitener, creating objects to populate the ```optimizer```, ```output_manager```, ```freqs```, and ```lcs``` attributes. Loads the default configuration, and overwrites it with configuration entries specified through ```cfg_file``` or ```cfg``` arguments.

**Args:**

* ```numpy.array time``` | An array containing the time axis of the input time series
* ```numpy.array data``` | An array containing the data axis of the input time series
* ```numpy.array err``` | Optional. An array containing weights for the data axis of the input time series. If unspecified, equal weights are assumed.
* ```string cfg_file``` | A path to a .toml file with configuration entries. The file does not have to be complete, and overwrites entries in the default configuration. Searches first in the current working directory, then in the package cfg directory, then for the absolute path. See https://pywhiten.readthedocs.io/en/latest/configuration/ for more details.
* ```dict cfg``` | A dictionary containing configuration entries. Does not have to be complete, and overwrites entries in both the default configuration and those provided via ```cfg_file```. See https://pywhiten.readthedocs.io/en/latest/configuration/ for more details.

____

#### ```id_peak(method: string, min_prov_sig, idx)```
Identifies a candidate frequency-amplitude pair in the periodogram corresponding to a light curve with the specified index. Also see documentation for the ```Periodogram``` object [here](https://pywhiten.readthedocs.io/en/latest/module-data/#select_peakmethod-str-min_prov_sig-float-mask-nparray).

**Args:**

* ```string method``` | The method to use for peak selection. Can be any of the following: ```["highest", "slf", "poly"]```. Specifying ```"highest"``` will result in the selection of a candidate frequency-amplitude pair according to the highest amplitude value on the periodogram. ```slf``` and ```poly``` provide methods of imposing an additional provisional significance criterion on the selected peak, where either an SLF model or low-order polynomial (fit in log-log space) is used to estimate the periodogram noise, and peak selection proceeds according to the highest amplitude peak that also exceeds the estimated noise function by ```min_prov_sig```.
* ```float min_prov_sig``` | Optional. The minimum provision signal-to-noise ratio for a peak to be accepted when using ```slf``` or ```poly``` methods.
* ```int idx``` | Optional. The index of the light curve to search within. This retrieves the light curve at index ```idx``` from ```lcs```, gets its periodogram, and searches within its periodogram for a peak. Default is -1, corresponding to the most recently added light curve.

**Returns:**

* ```float``` | A candidate frequency. ```None``` if no peaks satisfied the provisional significance criterion while using either ```slf``` or ```poly``` methods.
* ```float``` | A candidate amplitude. ```None``` if no peaks satisfied the provisional significance criterion while using either ```slf``` or ```poly``` methods.

___

#### ```it_pw(peak_selection_method: string)```
Conducts a single pre-whitening iteration. Identifies a candidate frequency/amplitude from the most recent light curve, fits a single-frequency sinusoid to the most recent light curve and includes it as a frequency,improves all parameters of all frequencies in multi-frequency fit against original light curve, and makes a new light curve ready for another iteration. A new frequency will be added to the end of ```freqs```, and a new lightcurve will be added to the end of ```lcs```. ```output_manager.save_it()``` is called as well, outputting data and plots to the output directory.

**Args:**

* ```string peak_selection_method``` | Optional. Sets the peak selection method. See ```id_peak``` above.

**Returns:**

* ```int``` | A flag.
    * 0 if iteration succeeded
    * 1 if peak identification failed using the specified method
    * 2 if a new lightcurve couldn't be generated. Check autopw.new_lc_generation_method in config.

___

#### ```it_pw_manual(frequency: float, amplitude: float, phase: float)```
Conducts a single pre-whitening iteration. Using the manually-specified frequency/amplitude/phase hints, fits a single-frequency sinusoid to the most recent light curve and includes it as a frequency,improves all parameters of all frequencies in multi-frequency fit against original light curve, and makes a new light curve ready for another iteration. A new frequency will be added to the end of ```freqs```, and a new lightcurve will be added to the end of ```lcs```. ```output_manager.save_it()``` is called as well, outputting data and plots to the output directory.

**Args:**

* ```string peak_selection_method``` | Optional. Sets the peak selection method. See ```id_peak``` above.

**Returns:**

* ```int``` | A flag.
    * 0 if iteration succeeded
    * 1 if peak identification failed using the specified method
    * 2 if a new lightcurve couldn't be generated. Check autopw.new_lc_generation_method in config.

___

#### ```post_pw(residual_lc_idx : int)```
Conducts some post-prewhitening tasks. Evaluates significances, computes parameter uncertainties, and saves some final data/plots.

**Args:**

* ```int residual_lc_idx``` | Optional. The light curve to treat as the residual light curve. In most cases, this should be -1, which is also the default value (and retrieves the last light curve in ```lcs```).