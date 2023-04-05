# Configuration

Pywhiten, and particularly its auto-prewhitening functionality, is highly configurable and flexible to suit application with a variety of time series data. This is achieved through use of an instance-based configuration system, where a configuration is loaded for each individual data set under analysis. A set of configuration options is specified in a .toml file, which is loaded to a dictionary and stored as an attribute of the Pywhitener objects. The user can partially or fully specify their desired configuration state through a .toml file or a dictionary passed as a constructor argument to Pywhiten. The default configuration is available in the package directory under cfg/default.toml.

The path to the package can be retrieved in the following package variable:
```
import pywhiten
print(pywhiten.pkg_path)
```

Perhaps more useful, a copy of the default configuration file can be made at a user specified location as follows:
```
import pywhiten
pywhiten.make_config_file(str:path)
```
If the user doesn't specify a path (calls the function with no arguments), the default configuration copy is made at `./default.toml`.

## TOML Configuration
Pywhiten uses [Tom's Obvious Minimal Language (TOML)](https://toml.io/en/) for configuration file formats. If you're not familiar with TOML, you can refer to its specification [here](https://toml.io/en/v1.0.0). It should be sufficient in all forseeable cases to simply copy and modify the default configuration, however if you're having issues you suspect may be related to syntax that's a good place to start.

When a pywhiten object is initialized, a filename for a configuration file can be optionally specified:

```
example_pywhitener = Pywhitener(time, data, err, cfg_file = "myconfig.toml")
```

The constructor searches in the working directory then the package's /cfg/ directory for a file with the specified name. Alternatively, a full path to a configuration file can be specified, which is checked last. The TOML file is loaded to a python dictionary using tomli and is stored as an attribute (Pywhitener.cfg) of the Pywhitener object.

## Dictionary Configuration
As the package simply uses tomli to convert a ```.toml``` file to a Python dictionary, it also offers the opportunity to provide a Python ```dict``` object instead of a ```.toml``` file. Here is an example of doing this:
```
example_pywhitener = Pywhitener(time, data, err, cfg = my_dict)
```
The dictionary must be structured similarly to the .toml file, which is how tomli loads them in. That is, if you consider how items are structured in the TOML specification, they are given as their name preceeded by all subcategories divided by periods. For example, x labels of light curve plots are ```plots.lightcurves.x_label```. When converted to a Python dictionary object, this becomes a nested dictionary structure where the value is accessible via ```my_dict["plots"]["lightcurves"]["x_label"]```. For the input data axis unit, ```input.flux_unit```, this is instead  which is accessible via ```my_dict["input]["flux_unit"]```. For further information, please refer to the [tomli documentation](https://pypi.org/project/tomli/).

## Configuration from multiple sources
Pywhiten does not require that you fully specify the configuration in a single file or dictionary. In fact, you can source entries from all of the default configuration, a dictionary, and a file. These are loaded in the following order:
1. Default Configuration
2. File Configuration
3. Dictionary Configuration

Conflicting entries are overwritten at each step, so entries from a dict take precedence over a file, and file entries take precedence over the default. This ensures the configuration is always fully specified and also provides the user with the flexibility to make their own partial configuration files as well as directly override configuration settings at instantiation of a Pywhitener.


## Config Structure

Configuration options are structured into six categories as follows:

1. [input](#input) | Data loading and characteristics.
2. [output](#output) | Outputs to both stdout and the results directory.
    1. [output.paths](#outputpaths) | Structure of results directory.
    2. [output.debug](#outputdebug) | Debug printing options.
3. [plots](#plots) | Plot formatting and saving.
    1. [plots.periodograms](#plotsperiodograms) | Labels for periodogram plots.
    2. [plots.lightcurves](#plotslightcurves) | Labels for lightcurve plots.
4. [periodograms](#periodograms) | Settings for computation of periodograms.
5. [autopw](#autopw) | Options relating to automatic pre-whitening, including cutoff significances.
    1. [autopw.bounds](#autopwbounds) | Boundaries on parameter types when performing multi-frequency fits.
6. [optimization](#optimization) | Settings relating to how optimization steps are performed.

The individual options and their datatypes and descriptions are as follows:

### Input
    
* ```string flux_unit = "unknown"```: input data axis unit. Uncertainties are assumed to be in this unit. If you are inputting data in magnitude or millimagnitude, enter ```"mag"``` or ```"mmag"```. It will be converted to a linear unit for analysis, however may be output in mmag by setting the output.plot_output_in_mmag or output.data_output_in_mmag flag to true.
* ```string time_unit = "unknown"```: input time axis unit.
* ```float input_t0 = 0```: if the time axis is relative to some value (e.g. ```JD-2457000```, for TESS data), set it here and it'll be corrected (added to all time axis values)
* ```float measurement_t0 = 0```: subtracted from the time axis prior to analysis. Useful if you want to measure your phases with respect to some time value
* ```subtract_mean = true```: set this to subtract the mean of the light curve when data is loaded. If the mean of the light curve isn't zero or very close to it, then there will be a large apparant amplitude component near 0 frequency which will probably cause problems.


### Output
* ```bool print_runtime_messages = true```: prints messages during runtime indicating the pre-whitening progress
* ```bool plot_output_in_mmag = false```: if you'd like output plots in mmag, set this to true. This was implemented in previous iterations of the program, however is currently untested and will likely be deprecated or reworked.
* ```bool data_output_in_mmag = false```: if you'd like output data in mmag, set this to true (incl reported frequencies
* ```float reference_flux = 1```: the reference flux corresponding to the reference magnitude, used for conversions from magnitude to flux and vice-versa. Due to the nature of the magnitude system, it requires a reference point. Typically, this has been the star Vega, however magnitude systems are highly nonstandard and this isn't always the case.
* ```float reference_mag = 1```: the reference magnitude corresponding to the reference flux.
#### Output.paths
* ```clean_dirs = false```: if true, cleans the output base directory. ANYTHING UNDER BASE WILL BE REMOVED.


There are numerous string entries in this subcategory defining the names of folders in the results folder. This heirarchy is shown below.
* ```base```: The results folder location
    * ```pgs_base```
        * ```pgs_raw```
        * ```pgs_slf```
        * ```pgs_lopoly```
        * ```pgs_data```
    * ```lcs_base```
        * ```lcs_raw```
        * ```lcs_sf```
        * ```lcs_mf```
        * ```lcs_data```
    * ```auxiliary```
#### Output.debug
* ```print_debug_messages = false```: prints debug messages during.
* ```show_peak_selection_plots = false```: Shows diagnostic plots during runtime at the peak selection stage.


### Plots
* ```bool save_periodogram_plots = true```: Sets whether to save plots of periodograms. Not saving the plots can save significant disc space, if that is of concern. However, these are useful to visualize the process and diagnose any issues or unexpected behaviour.
* ```bool save_lightcurve_plots = true```: Sets whether to save plots of lightcurves. Not saving the plots can save significant disc space, if that is of concern. However, these are useful to visualize the process and diagnose any issues or unexpected behaviour.
#### Plots.periodograms

* ```string x_label = "Frequency \[cycles/%input.time_unit%\]"```: x labels for periodograms. Custom formatting not implemented yet.
* ```string y_label = "Amplitude \[%input.data_unit%\]"```: y labels for periodograms. Custom formatting not implemented yet.
#### Plots.lightcurves]
* ```string x_label = "Time \[%input.time_unit%\]"```: x labels for light curves. Custom formatting not implemented yet.
* ```string y_label = "Flux \[%input.data_unit%\]"```: y labels for light curves. Custom formatting not implemented yet.
### Periodograms
* ```float, string lower_limit = "resolution"```: Sets lower limit in frequency for periodogram computation. Can be "resolution" or non-negative float.
* ```float, string upper_limit = 20```:  # Sets upper limit in frequency for periodogram computation. Can be "nyquist" or non-negative float greater than lower_limit.
* ```integer points_per_resolution_element = 20```: number of points per unit in frequency. If the time series is specified in days, \[f\] = \[c/d\]
* ```polyfit_order = 5```: sets the order of polynomial to use when fitting a polynomial to periodograms

### AutoPW
* ```string peak_selection_method = "slf"```: Method of assessing provisional significances. Only ```"slf"``` is tested right now, corresponding to a stochastic low-frequency variability (red noise+white noise) fit, but ```"poly"``` should also work (corresponding to a low order polynomial fit to the log-log periodogram). This can also be set to ```"highest"```, which will select the highest amplitude peak repeatedly until reaching cutoff_iteration. ```"slf"``` should work best for most cases.
* ```string new_lc_generation_method = "mf"```: dictates how to generate new light curves in the final stage of each pre-whitening iteration. "mf" subtracts the multi-frequency fit from the original light curve, while "sf" subtracts the single-frequency model from the most recent light curve.
* ```int peak_selection_highest_override = 10```: number of frequencies to extract via highest peak before using the specified peak selection method. This can be useful if your light curve has some particularly strong frequencies and you're trying to access the weaker ones.
* ```float peak_selection_cutoff_sig = 4.0```: the minimum significance for peak acceptance if using slf or bin peak_selection.
* ```int cutoff_iteration = 50```: maximum number of frequencies to extract regardless of achieving the termination criterion. If peak_selection_method is set to ```"highest"```, this is the number of frequencies that will be extracted.
#### AutoPW.bounds
* ```float phase_fit_rejection_criterion = 0.1```: if a phase parameter from a single-frequency fit is within this value of the initial guess, adjust the initial guess and try again until it isn't. This should avoid help avoid local chi squared minima in phase. Note that the adjustment is fixed at a value of 0.17.
* ```float freq_lower_coeff = 0.8```:  Sets lower bound on each frequency parameter f_init to f_init * freq_lower_coeff for multi-frequency fits
* ```float freq_upper_coeff = 1.2```:   Sets upper bound on each frequency parameter f_init to f_init * freq_upper_coeff for multi-frequency fits
* ```float amp_lower_coeff = 0.8```: Sets lower bound on each amplitude parameter amp_init to amp_init * amp_lower_coeff for multi-frequency fits.
* ```float amp_upper_coeff = 1.2```:  Sets upper bound on each amplitude parameter amp_init to amp_init * amp_upper_coeff for multi-frequency fits
* ```float phase_lower = -100```:  Sets an absolute lower limit on all phase values for multi-frequency fits.
* ```float phase_upper = 100```: Sets an absolute upper limit on all phase values for multi-frequency fits.
### Optimization
* ```string optimization_pkg = "lmfit"```: The optimization package to use for all optimizations. Currently only ```"lmfit"``` works, which provides a slightly modified implementation of MINPACK which handles bounds more gracefully. Previously, ```"scipy"``` also worked, however the implementation of boundaries in scipy was causing some issues.
* ```bool mf_include_zp = true```: Includes a constant zero point offset in multi-frequency fits if set. This means that a multi-frequency fit has (Number of Frequencies) * 3 + 1 parameters.
* ```float mf_boundary_warnings = 0.05```: Warns user if multi-frequency fit values are within a factor of this (e.g. if ```value * mf_boundary_warnings > abs(value - boundary)```) of the boundaries. Set to 0 to disable.
* ```bool sf_phase_value_check = true```: Enables a check to see if phase significantly moved during single-frequency fit. If not, it's possible we're stuck in a local minimum and we should adjust our initial guess and try again.
* ```string frequency_model_type = "sin"```: sets whether to use a sin or cos function for the sinusoidal model. Can be ```"sin"``` or ```"cos"```. Useful if you're comparing with results from another analysis which used one or the other.
