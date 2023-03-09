import numpy as np

def flux2mag(data, ref_flux, ref_mag):
    """ Converts a data array with reference flux ref to magnitude"""
    return -2.51188643151 * np.log10(data/ref_flux) + ref_mag

def flux2mag_e(data, ref_flux, ref_mag, err):
    """ Converts a data array with reference flux ref to magnitude, including error propagation"""
    mag = -2.51188643151 * np.log10(data/ref_flux) + ref_mag
    err = (-2.51188643151/np.log(10))*err/data
    return mag, err

def format_output(n, e, npts):
    """
    Formats a measurement of the form 1.23 +/- 0.01 as 1.23(1).
    Args:
        n (float): a nominal value of a measurement
        e (float): an error corresponding to the nominal value
        npts (int): Number of digits in uncertainty to retain

    Returns:
        formatted string
    """
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

