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
    _flist: list = []

    def __init__(self, *freqs):
        for i in range(len(freqs)):
            if type(freqs[i]) != Frequency:
                raise InvalidContructorArgumentsError("FrequencyContainer initialized with at least one argument not"
                                                      "of type Frequency")
        self._flist = [*freqs]

    def get_flist(self):
        """
        Getter for frequency list, which shouldn't be direct accessed by user
        Returns:
            list: List of frequencies
        """
        return self._flist

    def mf_model(self, time, zp:float = 0):
        y = np.zeros(len(time))
        for f in self._flist:
            y += sin_model(time, *f.get_parameters())
        return y+zp

    def get_last_frequency(self):
        """
        Gets the frequency on the end of the flist
        Returns:
            Frequency: the most recently-added frequency in flist
        """
        return self._flist[-1]

    def add_frequency(self, freq:Frequency):
        self._flist.append(freq)