# phmin

A basic python package for determining periods in time series data through phase dispersion minimization.  
Author: Erik William Stacey  
Date: 7 Feb, 2023  

## Installation

phmin is available through pip:  
```
pip install phmin
```
Or, alternatively, download and install directly from this repo:  
```
git clone https://github.com/erikstacey/phmin.git ./phmin
cd phmin
pip install .
```

## Usage

The ph_minner class is used to store and operate on time series data. Here's a basic example snippit setting up a ph_minner:  
```
import numpy as np
from phmin import ph_minner

x, y, y_err = np.loadtxt("sample.txt", unpack=True)
example_minner = ph_minner(x=x, y=y, err=y_err)
```

To run the minimizer, call the run method:  
```
example_minner.run()
```

To print or plot the results, call  

```
example_minner.print_results()
example_minner.plot_results()
```

## Advanced Usage
In most cases, the user will want to specify the bin widths and number of bins in accordance with the characteristics of
the time series under examination. These are set through the optional parameters of the ph_minner class ```nb``` and ```nc```:  

```
example_minner = ph_minner(x=x, y=y, err=y_err, nb = 10, nc=4)
```

The ```nb``` and ```nc``` parameters are unintuitive as how they control the phase binning. Firstly, the bin width is
equivalent to ```1/nb```, and the total number of bins is equivalent to ```nb*nc```. As the bins must remain within```[0,1]```,
setting ```nc>1``` will result in overlapping bins with bin centers evenly spaced by ```1/(nb*nc)``` and wrapping around
the edges of the phase interval ```[0,1]```. The default parameters set ```nb=5, nc=2```, resulting in 10 0.2-width bins.  

The ph_minner class can also be initialized with optional parameters periods and t0. Setting periods manually defines the period grid, and setting t0 manually sets the reference time for the phasing.  

```
manual_period_grid = np.linspace(4.4, 4.8, 500)
example_minner = ph_minner(x=x, y=y, err=y_err, periods=manual_period_grid, t0=2457000.0)
```

The results can be directly accessed through attributes of the ```ph_minner``` class.  
```ph_minner.periods``` - Array of periods  
```ph_minner.thetas``` - Array of theta values. See [Stellingwerf (1978, ApJ, 224, 953)](https://ui.adsabs.harvard.edu/abs/1978ApJ...224..953S/abstract) and 
[Schwarzenberg-Czerny (1997, ApJ, 489(2), 941)](https://ui.adsabs.harvard.edu/abs/1997ApJ...489..941S/abstract) for details.

```
best_P, min_theta = ph_minner.best_fit_pars()
```

This package also includes a class ```ls_ph_minner```, which operates similarly to the phase dispersion minimizer. However
this class actually relies on chi squared minimization of a sinusoidal variability model against the phased data at each candidate
period, making it statistically equivalent to a Lomb-Scargle analysis (and functionally different from a phase dispersion
minimization analysis). This is useful for quickly identifying a single sinusoidal frequency in spaced data, 
however for LS frequency analysis my [PyPreW](https://github.com/erikstacey/PyPreW) package is significantly more capable.  


## Method
This package is intended to solve the problem of determining the principal frequency present in time series data through 
phase dispersion minimization. During the initialization process, a set of candidate periods are either user-provided
or generated. A set of (overlapping, for nc>1) bins in phase are also generated. When the run method is called, it
iterates over all candidate frequencies and at each iteration it:
1) Converts the timeseries time stamps to phases,
2) Evaluate the variance in each bin,
3) Compare the bin variances against the total variance in the time series to yield the theta parameter,
4) Stores the theta parameter to later identify which candidate period had the minimal theta.

More details on the phase dispersion minimization methodology are presented by 
[Stellingwerf (1978, ApJ, 224, 953)](https://ui.adsabs.harvard.edu/abs/1978ApJ...224..953S/abstract). Also
see [Schwarzenberg-Czerny (1997, ApJ, 489(2), 941)](https://ui.adsabs.harvard.edu/abs/1997ApJ...489..941S/abstract) for
an updated statistical treatment of this method.

### Changelog
V1.0.0 (7 Feb, 2023)  
-Changed ph_minner to implement phase dispersion minimization
-Moved previously-placeholder Lomb-Scargle equivalent functionality to ls_ph_minner

V0.1.4 (6 Feb, 2023)  
-Fixed plot_results()

V0.1.3 (6 Feb, 2023)  
-Removed redundant fmt in plot_results()

V0.1.2 (6 Feb, 2023)  
-Fixed label in ph_minner.plot_results()

V0.1.0 (6 Feb, 2023)  
-Added methods to ph_minner for printing and plotting results
-Throws an exception if the user tries to plot or print without running first

V0.0.1 (6 Feb, 2023)  
-Working package published on github