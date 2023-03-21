![##PyWhiten](pywhitenlogo3.png)

A python package for conducting Lomb-Scargle-based pre-whitening of time series data.

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
The general documentation is available [here](https://pywhiten.readthedocs.io/en/latest/), and a getting started guide is available [here](https://pywhiten.readthedocs.io/en/latest/getting-started)

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






