import numpy as np

def flux2mag(data, ref):
    """ Converts a data array with reference flux ref to magnitude"""
    return -2.5 * (np.log10(data + ref) - np.log10(ref))

def flux2mag_e(data, ref, err):
    """ Converts a data array with uncertainties and a reference flux to magnitude."""
    mag = -2.5*(np.log10(data+ref) -np.log10(ref))
    mag_err = abs(-2.5 * err / ((data + ref) * np.log(10)))
    return mag, mag_err

def format_output(n, e, npts):
    split_n = str(n).split('.')
    split_e = str(e).split('.')
    roundto = 0
    if len(split_n) == 1: # int
        pass
    elif len(split_n) == 2: # float
        error_decimal = split_e[1]
        for i in range(len(error_decimal)):
            if error_decimal[i] != "0":
                roundto = i + npts
                while len(error_decimal) < roundto:
                    error_decimal += "0"
                break

        err_out = error_decimal[roundto-npts:roundto]
        return f"{n:.{roundto}f}({err_out})"

