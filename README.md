![##PyWhiten](pywhitenlogo3.png)

A python package for conducting Lomb-Scargle-based pre-whitening of time series data.

## Installation

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

## Getting Started
See the readthedocs page [here](https://pywhiten.readthedocs.io/en/latest/getting-started)

## Documentation
View the readthedocs [here](https://pywhiten.readthedocs.io/en/latest/)

## Methodology and Implementation

This package is principally designed for automated or semi-automated frequency analysis. More specifically, a type of
pre-whitening analysis is conducted iteratively to quantitatively identify sinusoidal signals present in time series
data (for time series with non-sinusoidal signals, a technique like Phase Dispersion Minimization may be more suitable;
see [phmin](https://github.com/erikstacey/phmin)).

# Basics of Pre-Whitening

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

# Pywhiten Implementation

A significant portion of the work that went into developing this package was in testing specific implementations of the basic process outlined above.
The objective of this testing was to design a procedure that could identify weaker signals in a time series dominated by a very strong harmonic structure,
which is the case for the photometric time series data for the star HD 47129 (Plaskett's Star). It was found that, instead of just optimizing each single-frequency sinusoidal model
as they are identified, performing a second optimization step where the parameters of all previously-identified frequencies are allowed to vary with the addition of the new single-frequency model. The final scheme for each iteration is as follows:
1) Compute a Lomb-Scargle periodogram using the AstroPy.timeseries package
2) Identify a candidate frequency/amplitude
   - For the first n iterations, where n was typically taken to be 10, the candidate frequencies/amplitudes were measured as simple the highest peak on the periodogram
   - For iterations after the nth, the candidate frequencies/amplitudes were measured as the highest peak in the periodogram that also exceeded a provisional significance criterion (3 sigma), measured by performing a fit of a red+white noise model to the periodogram
   - If no values in the periodogram exceed the provisional significance criterion, the analysis is concluded
3) Perform a single-frequency model optimization to the light curve with the candidate frequency/amplitude used as initial values (and a provisional phase of 0.5)
4) Add the optimized single-frequency model to the complete variability model, consisting of all identified frequencies. Allow all parameters of this model to vary and perform an optimization against the original (non-residual) light curve
5) Subtract the complete variability model from the original light curve to generate a residual light curve. This is passed to the next iteration and used to determine a new single-frequency model.

This approach has some significant drawbacks:

1) With the addition of each single-frequency model, the multi-frequency model gains 3 parameters. Therefore, a 50-frequency model has a minimum of 150 free parameters, some of which may be partially corrolated.
   - This approach works best when working with 30 or less frequencies
2) Allowing the frequencies to vary in the multi-frequency fit can cause the optimization to fail. Pywhiten implements two safeguards against this, which generally prevent anomalous results or runtime failures:
   1) New frequencies are not selected within 1.5/T of existing frequencies, where T is the total time baseline of the dataset. This is the (empirical) minimum separation between two frequencies necessary to make reliable independent measurements of each of them.
   2) As the multi-frequency fit is intended as a refinement step, where parameters shouldn't change significantly, frequencies and amplitudes are bounded by default to a small region around their initial values.
3) Related to (1), the additional refinement step can increase computation time significantly.





