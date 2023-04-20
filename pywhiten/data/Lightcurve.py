import numpy as np
from pywhiten.data.InvalidConstructorArgumentsError import InvalidContructorArgumentsError
from pywhiten.data.Periodogram import Periodogram
import matplotlib.pyplot as pl

class Lightcurve():
    """
    An object storing a time series.
    Attributes:
        time : np.array
            Time indexes of measurements
        data : np.array
            Measurements indexed by the time array
        err : np.array
            Measurement uncertainties on data
        periodogram : Periodogram
            The object storing the frequency spectrum of this time series
    """
    time = None
    data = None
    err = None
    periodogram = None


    def __init__(self, time, data, err = None, cfg = None):
        if (type(time) not in [list, np.ndarray, tuple]) or (type(data) not in [list, np.ndarray, tuple]):
            raise InvalidContructorArgumentsError("Lightcurve initialized with time or data not of type list, tuple,"
                                                  "or ndarray")
        else:
            self.time = np.array(time)
            self.data = np.array(data)

        if err is None :
            self.err = np.ones(len(time))
        elif type(err) in [list, np.ndarray, tuple]:
            self.err = np.array(err)
        else:
            raise InvalidContructorArgumentsError("Lightcurve initialized with errors not of type list, tuple, ndarray,"
                                                  "or none")
        if cfg is None:
            self.periodogram = Periodogram(self.time, self.data)
        else:
            self.periodogram = Periodogram(self.time, self.data, cfg=cfg)


    def unpack(self):
        """
        Gets the time, data, and err arrays.
        Returns:
            np.ndarray: the time array
            np.ndarray: the data array
            np.ndarray: the measurement weights
        """
        return self.time, self.data, self.err

    def measure_N_eff(self):
        """
        Get the number of sign changes in the light curve. This is intended for use with differential lightcurves.
        Returns:
            int: the number of sign changes in the light curve.
        """
        sign_change_count = 0
        for i in range(len(self.time)-1):
            if (self.data[i]>0 and self.data[i+1]<0) or (self.data[i]<0 and self.data[i+1] > 0):
                sign_change_count+=1
        return sign_change_count

    def std(self):
        """
        Get standard deviation of light curve data
        Returns:
            float : std of light curve data axis
        """
        return np.std(self.data)

    def t_span(self):
        """
        Get the time span of the lightcurve
        Returns:
            float : max time value minus minimum time value
        """
        return max(self.time) - min(self.time)

    def debug_plot(self):
        pl.plot(self.time, self.data, linestyle=None, marker=".", color="black", markersize = 2)
        pl.show()
        pl.clf()


