![##PyWhiten](docs/img/pywhitenlogo3.png)

A flexible python package for conducting Lomb-Scargle-based pre-whitening of time series data. It is distinguished from other, similar tools by a focus on automated pipeline-style analysis and a high degree of flexibility through its extensive [configuration](https://pywhiten.readthedocs.io/en/latest/configuration/) system.

Written by [Erik Stacey](https://www.erikstacey.com/)

Updated 19 April 2023.

# Installation

pywhiten is available through pip:  
```
pip install pywhiten
```
Or, alternatively, download and install directly from this repo:  
```
git clone https://github.com/erikstacey/pywhiten.git ./pywhiten
cd pywhiten
pip install .
```


# Documentation
The general documentation is available [here](https://pywhiten.readthedocs.io/en/latest/), and a getting started guide is available [here](https://pywhiten.readthedocs.io/en/latest/getting-started) or in the next section.
# Getting Started
Pywhiten was designed to be easy to get up and running quickly out of the box, so let us walk through a tutorial example.
## Setting up a tutorial directory
First, lets create a tutorial directory somewhere:
```
mkdir pywhiten_tutorial
cd pywhiten_tutorial
```

Then, grab an example set of time series data [here](https://github.com/erikstacey/pywhiten/blob/master/Sample_Prewhitening_Directory/HD47129_thresh9_lc.txt) and
place it in a tutorial directory. Alternatively, you can provide your own time series data noting that the import examples may differ depending on your data format.
## Importing data and setting up a Pywhitener
To start pre-whitening, we need to load our time series data. But first, we need to create a python script. Here's an example with Vim, however you can use whatever you usually use to write python code:
```
vim example.py
```
Now, writing in our example script, we'll load our time series data into three arrays from the example file:
```
import numpy

time, data, err = np.loadtxt("HD47129_thresh9_lc.txt", unpack=True)
```

The Pywhitener class provides an easy-to-use interface to the rest of the package and powerful functionality for automated or semi-automated frequency analysis. Lets make one here by passing in the time series data we just loaded in:

```
pywhitener = pywhiten.PyWhitener(time=time, data=data, err=err)
```

Note that if you don't provide an error array, it will assume the data to be equally weighted. 

## Automatic Pre-Whitening

Now, running an automatic frequency analysis is as simple as calling the auto method:
```
pywhitener.auto()
```

This will automatically proceed through several iterations and, if using the sample data, will terminate after the 16th iteration after achieving the termination criterion. This will also
create a pw_out directory in the working directory and populate it with results. If you want to have a quick peek at the results, have a look at pw_out/frequencies.csv in your shell:
```
more ./pw_out/frequencies.csv
```

## Semi-automatic Pre-Whitening
If you want to proceed in single iterations only, you can do that with the it_pw() method of the pywhitener. Here's an example:

```
import numpy

time, data, err = np.loadtxt("HD47129_thresh9_lc.txt", unpack=True)
pywhitener = pywhiten.PyWhitener(time=time, data=data, err=err)
pywhitener.it_pw()
```
This will identify a single frequency. You can run this ten times to get ten frequencies:
```
for i in range(10):
   pywhitener.it_pw()
```
You can output this data to the pw_out directory using
```
pywhitener.post_pw()
```
Now, this example has so far used the default configuration for the program. Pywhiten derives its flexibility from its
configuration files, which make it possible to automate batch running frequency analyses on data from different instruments
with different configuration requirements. More details on the configuration can be found [here](https://pywhiten.readthedocs.io/en/latest/configuration)

## Directly Accessing Data and Results

If you'd like to directly access the results, that's easily accomplished through the attributes of the pywhitener.

### Light Curves

Light curves are stored in a list in the lcs attribute. Here's an example of accessing the residual lightcurve of the last iteration and plotting the results:
```
import matplotlib.pyplot as pl
residual_lc = pywhitener.lcs[-1]
pl.plot(residual_lc.time, residual_lc.data)
pl.show()
```
Refer to the documentation for what can be achieved using the Lightcurve objects.

### Periodograms

As periodograms are a description of the frequency spectrum of a time series, they are stored within the Lightcurve objects. Here's an example of accessing and plotting the residual periodogram:
```
import matplotlib.pyplot as pl
residual_lc = pywhitener.lcs[-1]
residual_periodogram = residual_lc.periodogram
pl.plot(residual_periodogram.lsfreq, residual_periodogram.lsamp)
pl.show()
```

### Frequencies

Unlike light curves, Frequency objects are stored in their own special container. A list of frequency objects can be acquired through a method of the FrequencyContainer object:
```
frequencies_list = pywhitener.freqs.get_flist()
print(f"The last identified frequency is at {frequencies_list[-1].f:.5f} with an amplitude of {frequencies_list[-1].a:.5f}!)
```

All of the Frequency, FrequencyContainer, Lightcurve, and Periodogram objects have useful functionality which is documented in the Data module of the docs!

# Methodology and Implementation

This package is principally designed for automated or semi-automated frequency analysis. More specifically, a type of
pre-whitening analysis is conducted iteratively to quantitatively identify sinusoidal signals present in time series
data (for time series with non-sinusoidal signals, a technique like Phase Dispersion Minimization may be more suitable;
see [phmin](https://github.com/erikstacey/phmin)).

## Basics of Pre-Whitening

This type of frequency analysis can be broadly defined by each iteration consisting of the following steps:

1) Compute an amplitude spectrum for the time series under examination
2) Identify a frequency/amplitude of interest
3) Perform a least squares optimization of a sinusoidal model to the time series, using the frequency/amplitude from step 1 as initial parameters
    - This will typically be a model of the form A*sin(2*pi*(f*x+p)), where f, A, and p represent a frequency, amplitude, and phase. This fully specifies a single-frequency sinusoidal model.
4) Subtract the optimized model from the time series to generate a residual time series 
   - This process can be repeated on the residual time series to identify another frequency

Following these steps will result in an optimized sinusoidal model for a single frequency, and a time series with that model removed. By
conducting this process many times, all the measurable periodic signals (including non-sinusoidal signals) can be extracted leaving, ideally,
a time series consisting only of the underlying noise.

## Motivation and Methodology of Pywhiten
When identifying a frequency model using a least-squares fit, the presence of other frequencies can make it more difficult to identify the model parameters (similar to how statistical fluctuations in data introduce
uncertainty in the parameters for models fit to that data). In a basic pre-whitening analysis, the residuals from one iteration are directly used in the next iteration to identify a new frequency and then generate new residuals.
Therefore, small fluctuations in model parameters will be propagated through each iteration and can significantly affect measurements only a handful of iterations deep. This effect is particularly pronounce when there is combination of
very high-amplitude and comparatively low-amplitude signals present, and can completely obscure the detection of the low-amplitude signals. 

Pywhiten was developed for a significant [research project](https://www.erikstacey.com/files/Stacey_MSc_thesis_finalversion_revised2.pdf) 
which focused on a comprehensive characterization of the photometric variability of a magnetic massive stellar binary system (HD 47129, Plaskett's Star).
This system demonstrates significant photometric variability due to the presence of a co-rotating centrifugal magnetosphere (CM) around the magnetic star,
which manifests as a high-amplitude harmonic structure in its power spectrum. Simultaneously, it has several comparatively low-amplitude signals which
are of scientific interest, made more challenging to detect by their proximity (in frequency) to the CM variability. Therefore, the problem we
sought to address was the detection of low-amplitude signals in time series with complex, dense power spectra dominated by a small number of high-amplitude frequencies.

An effective approach to the aforementioned problem was found in performing optimizations of a composite model containing
all the identified single-frequency sinusoidal models. Performing this at the end of a basic pre-whitening procedure is prone to
falling into a local chi^2 minimum, so we elected to include an aggressive refinement step at each iteration. This step occurs after
each single-frequency model fit and permits all frequencies/amplitudes/phases to vary in a fit to the original light curve. Therefore,
each Pywhiten iteration does the following:

1) Computes a Lomb-Scargle periodogram using the AstroPy.timeseries package,
2) Identifies a candidate frequency/amplitude.
3) Performs a single-frequency model optimization to the light curve with the candidate frequency/amplitude used as initial values (and a provisional phase of 0.5).
4) Adds the optimized single-frequency model to the complete variability model, consisting of all identified frequencies. Allows all parameters of this model to vary and perform an optimization against the original (non-residual) light curve.
5) Subtracts the complete variability model from the original light curve to generate a residual light curve. This is passed to the next iteration and used to determine a new single-frequency model.

Step (2) also has some special behaviour worth noting:
- For the first n iterations, where n was typically taken to be 10, the candidate frequencies/amplitudes were measured as simple the highest peak on the periodogram.
- For iterations after the nth, the candidate frequencies/amplitudes were measured as the highest peak in the periodogram that also exceeded a provisional significance criterion (3 sigma), measured by performing a fit of a red+white noise model to the periodogram.
- If no values in the periodogram exceed the provisional significance criterion, the analysis is concluded.

However, this is just the default behaviour based on the method presented in [this thesis](https://www.erikstacey.com/files/Stacey_MSc_thesis_finalversion_revised2.pdf), and is the recommended method for conducting pre-whitening on stellar time series data. This package
has been made to be reasonably flexible, and everything from the basic pre-whitening described prior and this process are possible.

### Drawbacks
The advantages of this method have been discussed in the motivation section above, but it's important to note that the additional complexity of this process has two significant drawbacks which
may preclude its suitability for some applications:
1) With the addition of each single-frequency model, the multi-frequency model gains 3 parameters. Therefore, a 50-frequency model has a minimum of 150 free parameters, some of which may be partially corrolated.
   - This approach works best when working with 30 or less frequencies. Computation time inflates significantly after .
2) Allowing the frequencies to vary in the multi-frequency fit can cause the optimization to fail. Pywhiten implements two safeguards against this, which are generally effective at preventing anomalous results or runtime failures:
   1) New frequencies are not selected within 1.5/T of existing frequencies, where T is the total time baseline of the dataset. This is the (empirical) minimum separation between two frequencies necessary to make reliable independent measurements of each of them.
   2) As the multi-frequency fit is intended as a refinement step, where parameters shouldn't change significantly, frequencies and amplitudes are bounded by default to a small region around their initial values.




## Change Log:

* 1.1.0 (April 21, 2023)
   * Fixed major bug with installion scripts while using pip where submodules would not be properly installed.
   * Moved the default configuration loading and access to new module ```cfg```. Default configuration can now be accessed through ```pywhiten.cfg.default_cfg```.
* 1.0.3 (April 5, 2023)
   * First non-internal release

