from astropy.timeseries import LombScargle
from typing import Union
import numpy as np
from scipy.optimize import curve_fit
from pywhiten.optimization.models import n_model_poly, slf_noise
import matplotlib.pyplot as pl


class Periodogram:
    """
    Class which stores and operates on a Lomb-Scargle periodogram.

    Attributes:
        lsfreq (ndarray): frequency axis of periodogram
        lsamp (ndarray): amplitude axis of periodogram
        slf_p (list): Parameter list describing stochasic low frequency model fit - Formatted as
        [x0, alpha_0, gamma, Cw]. See Bowman et al. (2019) for details on these parameters.
        slf_p_err (list): List of diagonal elements of the covariance matrix for the slf noise fit. Estimates of the
            uncertainties on the parameters contained in slf_p.
        p_approx_nyquist_f (float): The nyquist frequency assuming even sampling across the time baseline. This will NOT
            be the nyquist frequency for data with gaps, but it's the best way to handle the general case
            for automatically generating periodogram boundaries
        p_resolution (float): the minimum separation necessary to reliably resolve two periodic components close in
            frequency using a Lomb-Scargle-based pre-whitening methodology.
        log_polypar (ndarray): a list of coefficients for a polynomial fit in log-log space.
    """
    lsfreq = None
    lsamp = None
    log_polypar = None
    slf_p = None
    slf_p_err = None
    p_approx_nyquist_f = None
    p_resolution = None

    def __init__(self, time: np.ndarray, data: np.ndarray, lsfreq: Union[str, np.ndarray] = "auto",
                 fbounds: Union[str, tuple] = "auto", pts_per_res: int = 20):
        """
        Constructor for Periodogram class
        Args:
            time (ndarray): Time axis of time series
            data (ndarray): Data axis of time series
            lsfreq (str, ndarray): Frequency grid to compute the periodogram over. Default behaviour is "auto" which
                automatically generates a grid. Alternatively, an array of floats may be provided directly.
            fbounds (str, tuple): bounds for periodogram in frequency. "auto" automatically generates bounds based
                on the frequency resolution and nyquist frequency. If fgrid is specified, removes values outside
                the fbounds.
            pts_per_res (int): number of points to generate per resolution element. Ignored if fgrid is provided.
        Returns:
            Nothing
        Raises:
            TypeError: If input values aren't matched to the allowable types
        """
        # frequencies within this value are indistinguishable in this type of analysis
        self.p_resolution = 1.5 / (max(time) - min(time))
        # approximate nyquist frequency
        self.p_approx_nyquist_f = len(time) / (2 * (max(time) - min(time)))
        if lsfreq == "auto":
            if fbounds == "auto":
                # auto generate bounds from the resolution element to the approximate nyquist frequency.
                # This will probably include way too much superfluous information for most use cases.
                # That's the price of "auto".
                op_bounds = [self.p_resolution, self.p_approx_nyquist_f]
            else:
                if type(fbounds) not in [tuple, list, np.ndarray]:
                    raise TypeError(f"Tried to initialize Periodogram with fbounds of type {type(fbounds)} (must be"
                                    f"tuple, list, or ndarray)")
                else:
                    op_bounds = fbounds

            self.lsfreq = np.linspace(op_bounds[0], op_bounds[1],
                                      int(pts_per_res * (op_bounds[1] - op_bounds[0]) / self.p_resolution))
        else:
            if type(fbounds) not in [list, np.ndarray]:
                raise TypeError(f"Tried to initialize Periodogram with lsfreq of type {type(lsfreq)} (must be"
                                f"list or ndarray)")
            else:
                self.lsfreq = lsfreq

        # generates pseudo-power spectrum
        lspower = LombScargle(time, data, normalization="psd").power(self.lsfreq)
        # normalizes the pseudo-power spectrum to an amplitude spectrum
        self.lsamp = 2 * (abs(lspower) / len(time)) ** 0.5

    def highest_ampl(self, excl_mask: np.ndarray = None):
        """
        Gets the frequency and amplitude of the highest peak in the periodogram
        Args:
            excl_mask (ndarray): A boolean array specifying indices (in lsfreq/lsamp) to ignore
        Returns:
            float: The frequency corresponding to the maximum amplitude on the periodogram
            float: The maximum amplitude of the periodogram
        """
        if excl_mask is None:
            excl_mask = np.ones(len(self.lsfreq), dtype=bool)
        filtered_lsamp = self.lsamp[excl_mask]
        filtered_lsfreq = self.lsfreq[excl_mask]
        ymax = np.argmax(filtered_lsamp)
        xatpeak = filtered_lsfreq[ymax]
        return xatpeak, filtered_lsamp[ymax]

    def _find_troughs(self, center):
        """
        Determine local minima on either side of a specified value
        Args:
            center (float): specified value

        Returns:
            int: index of lower local minimum (to the left of the peak)
            int: index of upper local minimum (to the right of the peak)
        """
        count = 2
        left_i, right_i = None, None
        while (not left_i) or (not right_i):
            count += 1
            # check for left trough
            if not left_i and (center - count == 0 or self.lsamp[center - count] >= self.lsamp[center - count + 1]):
                left_i = center - count + 1
            if not right_i and (
                    center + count == len(self.lsfreq) or self.lsamp[center + count] >= self.lsamp[center + count - 1]):
                right_i = center + count - 1
        if left_i < 0:  # ensure no wraparound
            left_i = 0
            if right_i > len(self.lsfreq):
                left_i = len(self.lsfreq)
        return left_i, right_i

    def _find_index_of_freq(self, t):
        """
        Finds the index of lsfreq holding the closest frequency to a specified frequency
        Args:
            t (): a specified frequency

        Returns:
            int: the index of lsfreq holding the closest frequency to t
        """
        c_arr = self.lsfreq
        lower_bound = 0
        upper_bound = len(c_arr)
        while True:
            mid_i = (upper_bound - lower_bound) // 2 + lower_bound
            if t > self.lsfreq[mid_i]:
                lower_bound = mid_i
            elif t <= self.lsfreq[mid_i]:
                upper_bound = mid_i
            if upper_bound - lower_bound <= 1:
                lower_diff = abs(self.lsfreq[lower_bound] - t)
                upper_diff = abs(self.lsfreq[upper_bound] - t)
                if lower_diff > upper_diff:
                    return upper_bound
                else:
                    return lower_bound
            else:
                return lower_bound

    def peak_sig_box(self, center_val_freq, freq_amp, bin_r=1.0):
        """
        Gets the significance of a peak by considering the average periodogram value around the peak. Should NOT be used
        to measure significance in a residual periodogram where the peak has already been extracted (use sig_box()
        instead)
        Args:
            center_val_freq (float): frequency corresponding to maximum amplitude of peak
            freq_amp (float): amplitude of peak
            bin_r (float): radius in frequency to average. If this is less than the width of the peak

        Returns:
            float: A measured significance for the input peak
        """
        center_i_freq = np.where(self.lsfreq == center_val_freq)[0][0]
        trough_left_i, trough_right_i = self._find_troughs(center_i_freq)
        # determine target frequencies on either side of peak
        lower_val_freq = self.lsfreq[center_i_freq] - bin_r
        upper_val_freq = self.lsfreq[center_i_freq] + bin_r

        if lower_val_freq > self.lsfreq[trough_left_i] or upper_val_freq < self.lsfreq[trough_right_i]:
            raise AverageRadiusTooNarrow("Peak width on at least one side exceeds the specified average radius.")

        # don't permit target frequencies outside the range spanned by lsfreq
        if lower_val_freq < 0:
            lower_val_freq = 0
        if upper_val_freq > max(self.lsfreq):
            upper_val_freq = max(self.lsfreq)

        # convert target frequencies to frequency indices
        lower_i_freq = self._find_index_of_freq(lower_val_freq)
        upper_i_freq = self._find_index_of_freq(upper_val_freq)

        if lower_i_freq < 0:
            lower_i_freq = 0
        if upper_i_freq > len(self.lsfreq):
            upper_i_freq = len(self.lsfreq)

        # average the lower and upper region then return
        lower_avg_region = self.lsamp[lower_i_freq:trough_left_i]
        upper_avg_region = self.lsamp[trough_right_i:upper_i_freq]
        total_avg_region = np.concatenate((lower_avg_region, upper_avg_region))
        avg_regions_avg = np.mean(total_avg_region)
        return freq_amp / avg_regions_avg

    def sig_box(self, center_val_freq: Union[float, np.ndarray], freq_amp: Union[float, np.ndarray], bin_r=1.0):
        """
        Find the significance of a periodic component model by comparing its amplitude against the average residual
        periodogram near its frequency.
        Args:
            center_val_freq (float): The frequency of the periodic component
            freq_amp (float): The amplitude of the periodic component.
            bin_r (float): The radius in frequency to average around center_val_freq
        Returns:
            float: A measured significance for the input periodic component
        """
        center_i_freq = self._find_index_of_freq(center_val_freq)
        # find values of edge frequencies
        lower_val_freq = self.lsfreq[center_i_freq] - bin_r
        upper_val_freq = self.lsfreq[center_i_freq] + bin_r
        # find left and right indices
        lower_i_freq = self._find_index_of_freq(lower_val_freq)
        upper_i_freq = self._find_index_of_freq(upper_val_freq)
        total_avg_region = self.lsamp[lower_i_freq:upper_i_freq]
        return freq_amp / np.mean(total_avg_region)

    def fit_lopoly(self, poly_order: int):
        """
        Fits the periodogram with a polynomial in log-log space and stores the coefficients in the
        attribute log_polypar
        Args:
            poly_order (int): The polynomial order to use in the model

        Returns:
            Nothing
        """
        p0 = np.ones(poly_order + 1)
        log10_lsfreq = np.log10(self.lsfreq)
        log10_lsamp = np.log10(self.lsamp)
        p, pcov = curve_fit(f=n_model_poly, xdata=log10_lsfreq, ydata=log10_lsamp, p0=p0)
        self.log_polypar = p

    def sig_poly(self, center_val_freq: Union[float, np.ndarray], freq_amp: Union[float, np.ndarray]):
        """
        Find the significance of a periodic component model by comparing its amplitude against a low-order polynomial
        fit to the log-log residual periodogram. Conducts an order-5 polynomial fit if a polynomial fit hasn't yet
        been conducted on this periodogram.
        Args:
            center_val_freq (float, ndarray): The frequency of the periodic component
            freq_amp (float, ndarray): The amplitude of the periodic component
        Returns:
            float: A measured significance for the input periodic component
        """
        if self.log_polypar is None:
            self.fit_lopoly(5)
        logfreq = np.log10(center_val_freq)
        logval = n_model_poly(logfreq, *self.log_polypar)
        return freq_amp / (10 ** logval)

    def fit_slf(self):
        """
        Fits the periodogram with a red noise + white noise model from Bowman et al. (2019). Stores the parameters in
        the attribute slf_p, and parameter uncertainties in slf_p_err
        Returns:
            Nothing
        """
        p0 = [0.5, np.mean(self.lsamp), 0.5, 0]
        p, covar = curve_fit(slf_noise, xdata=self.lsfreq, ydata=self.lsamp, p0=p0)
        self.slf_p = p
        self.slf_p_err = np.array([covar[i, i] for i in range(len(p))])

    def sig_slf(self, center_val_freq: Union[float, np.ndarray], freq_amp: Union[float, np.ndarray]):
        """
        Find the significance of a periodic component model by comparing its amplitude against a low-order polynomial
        fit to the log-log residual periodogram. Conducts an order-5 polynomial fit if a polynomial fit hasn't yet
        been conducted on this periodogram.
        Args:
            center_val_freq (float, ndarray): The frequency of the periodic component
            freq_amp (float, ndarray): The amplitude of the periodic component
        Returns:
            float: A measured significance for the input periodic component
                """
        if self.slf_p is None:
            self.fit_slf()
        model_at_val = slf_noise(center_val_freq, *self.slf_p)
        return freq_amp / model_at_val

    def select_peak(self, method: str = "highest", min_prov_sig: float = 3.0, mask: np.ndarray = None,
                    cutoff: int = 50):
        """
        Determines a frequency-amplitude pair suitable for a pre-whitening iteration. Note: 'avg' method currently not
        implemented and just returns highest.
        Args:
            method (string): Must be one of ['highest', 'slf', 'poly', 'avg']. 'highest' selects the frequency-amplitude
                pair strictly according to the highest amplitude in the periodogram. Each of the 'slf', 'poly', and
                'avg' methods impose an additional significance criterion that the highest peak must exceed, and which
                of the three chosen specifies how the significance is measured.
            min_prov_sig (float): The minimum significance that a prospective peak must exceed if using the "slf",
                "poly", or "avg" methods.
            mask (ndarray): Array of boolean values excluding regions from peak selection. These regions are still used
                to measure significances, if applicable.
            cutoff (int): The number of times to try finding a peak above the provisional significance level before
                aborting and returning Nones. Only applies to box_avg selecction.
        Returns:
            float: the selected frequency. None if method is set to one of "slf", "poly", or "avg" and a peak exceeding
                min_prov_sig cannot be found.
            float: the selected amplitude. None if method is set to one of "slf", "poly", or "avg" and a peak exceeding
                min_prov_sig cannot be found.
        """
        # set up a mask to exclude
        working_mask = np.ones(len(self.lsfreq), dtype=bool)
        if mask is not None:
            working_mask*=mask
        if method == "highest":
            return self.highest_ampl(excl_mask=working_mask)
        elif method == "slf":
            # we can just use the fit functions to dettermine a provisional noise level for all lsfreq values,
            # then use this to make a mask to pass to highest_ampl
            working_mask *= self.sig_slf(self.lsfreq, self.lsamp) > min_prov_sig
            return self.highest_ampl(excl_mask=working_mask)
        elif method == "poly":
            # we can just use the fit functions to dettermine a provisional noise level for all lsfreq values,
            # then use this to make a mask to pass to highest_ampl
            working_mask *= self.sig_poly(self.lsfreq, self.lsamp) > min_prov_sig
            return self.highest_ampl(excl_mask=working_mask)
        elif method == "avg":
            return self.highest_ampl(excl_mask=working_mask)
        else:
            raise InvalidMethodError(f"method={method} in select_peak not in the allowable options: highest, slf,"
                                     f"poly, avg")
    def debug_plot(self):
        pl.plot(self.lsfreq, self.lsamp, color="black")
        pl.show()
        pl.clf()


class InvalidMethodError(Exception):
    pass


class AverageRadiusTooNarrow(Exception):
    pass
