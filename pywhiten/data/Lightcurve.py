import numpy as np

class Lightcurve:
    """
    An object storing a time series.
    Attributes:
        time : np.array
            Time indexes of measurements
        data : np.array
            Measurements indexed by the time array
        err : np.array
            Measurement uncertainties on data
    """