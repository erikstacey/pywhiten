from pywhiten.data import Periodogram, Lightcurve
from pywhiten.data.Frequency import Frequency
from pywhiten.data.InvalidConstructorArgumentsError import InvalidContructorArgumentsError
from pywhiten.optimization.models import sin_model
import numpy as np

class FrequencyContainer:
    """
    An object for storing and operating on groups of frequencies

    Attributes:
        _flist : list
            List of Frequency objects
    """
    flist: list = []
    n = 0

    def __init__(self, *freqs):
        for i in range(len(freqs)):
            if type(freqs[i]) != Frequency:
                raise InvalidContructorArgumentsError("FrequencyContainer initialized with at least one argument not"
                                                      "of type Frequency")
        self.flist = [*freqs]
        self.n = len(self.flist)

    def get_flist(self):
        """
        Getter for frequency list, which shouldn't be direct accessed by user
        Returns:
            list: List of frequencies
        """
        return self.flist

    def mf_model(self, time, zp:float = 0):
        y = np.zeros(len(time))
        for f in self.flist:
            y += sin_model(time, *f.get_parameters())
        return y+zp

    def get_last_frequency(self):
        """
        Gets the frequency on the end of the flist
        Returns:
            Frequency: the most recently-added frequency in flist
        """
        return self.flist[-1]

    def add_frequency(self, freq:Frequency):
        self.flist.append(freq)
        self.n += 1

    def del_frequency(self, index):
        self.flist.pop(index)
        self.n -= 1

    def compute_significances(self, residual_periodogram:Periodogram, eval : tuple =("slf", "box", "poly")):
        """
        Computes significances for stored frequencies and stores them in class attributes for each frequency. Computes
        according to 3 methods and stores the results in separate class attributes by default.
        Args:
            residual_periodogram (Periodogram): A periodogram object, which is assumed to consist of noise in order to
                evaluate the signal to noise ratio of the frequencies. Typically, when conducting pre-whitening, the
                analyzer will remove all frequencies reasonably thought to be real and identifiable in the data then
                uses the residual periodogram to evaluate their confidence in their results.
            eval (tuple): A tuple of strings indicating which significance methods to use in the evaluation. By default,
                this calculates significances using a box average ("box), red noise model ("slf"), and low-order
                polynomial model ("poly") fit.

        Returns:
            Nothing
        """
        for i in range(len(self.flist)):
            if "slf" in eval:
                self.flist[i].sig_slf = residual_periodogram.sig_slf(self.flist[i].f, self.flist[i].a)
            if "box" in eval:
                self.flist[i].sig_box = residual_periodogram.sig_box(self.flist[i].f, self.flist[i].a)
            if "poly" in eval:
                self.flist[i].sig_poly = residual_periodogram.sig_poly(self.flist[i].f, self.flist[i].a)

    def compute_parameter_uncertainties(self, residual_light_curve:Lightcurve):
        """
        Compute uncertainties for frequency, amplitude, and phase parameters of stored frequencies. Uses Montgomery &
        Odonogue (1999) method, with Schwarzenberg-Czerny (multiple publications, see astronomer's guide to period
        searching, 2003) correction. This method is utilized in Degroote et al. (2009)
        Args:
            residual_light_curve (Lightcurve): A Lightcurve object, which is assumed to have no reasonably measurable
                frequency content remaining. Note that in many cases this may appear to have coherent variability,
                however this can arise from stochastic noise commonly seen in stellar light curves (see SLF noise).

        Returns:
            Nothing
        """
        N_eff = residual_light_curve.measure_N_eff()
        sigma_residuals = residual_light_curve.std()
        time_baseline = residual_light_curve.t_span()
        for i in range(len(self.flist)):
            self.flist[i].sigma_f = (6/N_eff) ** 0.5 * sigma_residuals / (np.pi * time_baseline * self.flist[i].a)
            self.flist[i].sigma_a = (2/N_eff) ** 0.5 * sigma_residuals
            self.flist[i].sigma_p = (2/N_eff) ** 0.5 * sigma_residuals / self.flist[i].a