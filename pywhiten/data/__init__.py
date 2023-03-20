"""
Defines data structures useful for the pre-whitening process, with useful self-contained behaviour.

The Lightcurve and Periodogram classes are useful for storing representations of the data under analysis. For example,
the Lightcurve class stores a time series and automatically generates a Periodogram object, representing a pseudo-
amplitude spectrum corresponding to the Lightcurve object. The Frequency class provides a full description of a
single-frequency variability model, including the frequency, amplitude, and phase parameters as well as the sinusoidal
model that was used to optimize it.

Typical workflow is to import a timeseries to a Lightcurve object, identify a
candidate frequency/amplitude pair using its Periodogram object, perform and optimization (see pywhiten.optimization),
and store the results in a Frequency object. If performing iterative pre-whitening to identify multiple frequencies,
it may also be useful to store all these values in a FrequencyContainer object. In most cases where the pre-whitening is
conducted manually, a regular list of Frequency objects will suffice.

Classes:
    Frequency
    FrequencyContainer
    Lightcurve
    Periodogram
"""

from pywhiten.data.Frequency import Frequency
from pywhiten.data.FrequencyContainer import FrequencyContainer
from pywhiten.data.Lightcurve import Lightcurve
from pywhiten.data.Periodogram import Periodogram