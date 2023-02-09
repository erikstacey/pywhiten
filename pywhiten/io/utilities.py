import numpy as np

def flux2mag(data, ref):
    """ Converts a data array with reference flux ref to magnitude"""
    return -2.5 * (np.log10(data + ref) - np.log10(ref))

def flux2mag_e(data, ref, err):
    """ Converts a data array with uncertainties and a reference flux to magnitude."""
    mag = -2.5*(np.log10(data+ref) -np.log10(ref))
    mag_err = abs(-2.5 * err / ((data + ref) * np.log(10)))
    return mag, mag_err

