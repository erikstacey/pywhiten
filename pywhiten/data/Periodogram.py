from astropy.timeseries import LombScargle
from typing import Union
import numpy as np
from scipy.optimize import curve_fit

import pywhiten
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
    cfg = None

    def __init__(self, time: np.ndarray, data: np.ndarray, lsfreq: Union[str, np.ndarray] = "auto",
                 fbounds = None,
                 pts_per_res: int = pywhiten.cfg.default_cfg["periodograms"]["points_per_resolution_element"],
                 cfg=None):
        """
        Constructor for Periodogram class
        Args:
            time (ndarray): Time axis of time series
            data (ndarray): Data axis of time series
            lsfreq (str, ndarray): Frequency grid to compute the periodogram over. Default behaviour is "auto" which
                automatically generates a grid. Alternatively, an array of floats may be provided directly.
            fbounds (tuple): bounds for periodogram in frequency of format (lower, upper)
            pts_per_res (int): number of points to generate per resolution element. Ignored if fgrid is provided.
            cfg (dict): A configuration dict. If nothing is provided, the default is used.
        Returns:
            Nothing
        Raises:
            TypeError: If input values aren't matched to the allowable types
        """
        if cfg is not None:
            self.cfg = cfg
        else:
            self.cfg = pywhiten.cfg.default_cfg
        # frequencies within this value are indistinguishable in this type of analysis
        self.p_resolution = 1.5 / (max(time) - min(time))
        # approximate nyquist frequency
        self.p_approx_nyquist_f = len(time) / (2 * (max(time) - min(time)))

        # set up a frequency grid. This is the most configurable component so it has a few branching paths for setup.
        if lsfreq == "auto":
            if fbounds is not None:  # explicitely provided bounds
                ll, ul = fbounds[0], fbounds[1]
            else:  # bounds not explicitely provided so they must be generated
                ll = self.cfg["periodograms"]["lower_limit"]
                if ll == "resolution":
                    ll = self.p_resolution
                ul = self.cfg["periodograms"]["upper_limit"]
            self.lsfreq = np.linspace(ll, ul, pts_per_res * int(abs(ll-ul)/(self.p_resolution)))
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

        # if the exclusion mask excludes all values from selection
        if len(filtered_lsamp) == 0:
            return None, None

        ymax = np.argmax(filtered_lsamp)
        xatpeak = filtered_lsfreq[ymax]
        return xatpeak, filtered_lsamp[ymax]

    def find_troughs(self, center):
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

    def find_index_of_freq(self, t):
        """
        Finds the index of lsfreq holding the closest frequency to a specified frequency
        Args:
            t (): a specified frequency

        Returns:
            int: the index of lsfreq holding the closest frequency to t
        """
        # just do linear search
        # this could be a binary search but it's not used all that often
        for i in range(len(self.lsfreq)-1):
            # check if t is between values at i, i+1
            if self.lsfreq[i] <= t < self.lsfreq[i+1]:
                # find out which one it is closer to
                if abs(self.lsfreq[i] - t) > abs(self.lsfreq[i+1] - t):
                    return i
                else:
                    return i+1
        print("[pywhiten][WARNING]: attempted to retrieve index of frequency outside of Periodogram lsfreq span")
        if t < self.lsfreq[0]:
            return 0
        else:
            return len(self.lsfreq)

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
        trough_left_i, trough_right_i = self.find_troughs(center_i_freq)
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
        lower_i_freq = self.find_index_of_freq(lower_val_freq)
        upper_i_freq = self.find_index_of_freq(upper_val_freq)

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
        center_i_freq = self.find_index_of_freq(center_val_freq)
        # find values of edge frequencies
        lower_val_freq = self.lsfreq[center_i_freq] - bin_r
        upper_val_freq = self.lsfreq[center_i_freq] + bin_r
        # find left and right indices
        lower_i_freq = self.find_index_of_freq(lower_val_freq)
        upper_i_freq = self.find_index_of_freq(upper_val_freq)
        total_avg_region = self.lsamp[lower_i_freq:upper_i_freq]
        return freq_amp / np.mean(total_avg_region)

    def fit_lopoly(self, poly_order: int = pywhiten.cfg.default_cfg["periodograms"]["polyfit_order"]):
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

    def sig_poly(self, center_val_freq: float, freq_amp: float):
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
        model_at_val = self.eval_slf_model(center_val_freq)
        return freq_amp / model_at_val

    def select_peak(self, method: str = "highest", min_prov_sig: float = 4.0, mask: np.ndarray = None):
        """
        Determines a frequency-amplitude pair suitable for a pre-whitening iteration. Note: 'avg' method currently not
        implemented and just returns highest.
        Args:
            method (string): Must be one of ['highest', 'slf', 'poly']. 'highest' selects the frequency-amplitude
                pair strictly according to the highest amplitude in the periodogram. Each of the 'slf', 'poly',
                 methods impose an additional significance criterion that the highest peak must exceed, and which
                of the three chosen specifies how the significance is measured.
            min_prov_sig (float): The minimum significance that a prospective peak must exceed if using the "slf",
                "poly" methods.
            mask (ndarray): Array of boolean values excluding regions from peak selection. These regions are still used
                to measure significances, if applicable.
            cutoff (int): The number of times to try finding a peak above the provisional significance level before
                aborting and returning Nones. Only applies to box_avg selecction.
        Returns:
            float: the selected frequency. None if method is set to one of "slf", "poly" and a peak exceeding
                min_prov_sig cannot be found. Also returns None if user provides a mask consisting of all False values
            float: the selected amplitude. None if method is set to one of "slf", "poly" and a peak exceeding
                min_prov_sig cannot be found. Also returns None if user provides a mask consisting of all False values
        """
        # set up a mask to exclude
        working_mask = np.ones(len(self.lsfreq), dtype=bool)

        if mask is not None:
            working_mask*=mask

        if method == "highest":
            pass
        elif method == "slf":
            # we can just use the fit functions to dettermine a provisional noise level for all lsfreq values,
            # then use this to make a mask to pass to highest_ampl
            working_mask *= self.sig_slf(self.lsfreq, self.lsamp) > min_prov_sig
            if self.cfg["output"]["debug"]["show_peak_selection_plots"]:
                self.peak_selection_debug_plot_slf(working_mask)
        elif method == "poly":
            # we can just use the fit functions to dettermine a provisional noise level for all lsfreq values,
            # then use this to make a mask to pass to highest_ampl
            working_mask *= self.sig_poly(self.lsfreq, self.lsamp) > min_prov_sig
        else:
            raise ValueError(f"method={method} in select_peak not in the allowable options: highest, slf,"
                                     f"poly, avg")

        if (~working_mask).all():  # this condition checks if the mask contains all false values
            return None, None
        else:
            return self.highest_ampl(excl_mask=working_mask)
    def eval_slf_model(self, x):
        """Performs a SLF fit if one hasn't been performed already,
        and evaluates the SLF model fit at the x value(s) provided."""
        if self.slf_p is None:
            self.fit_slf()
        return slf_noise(x, *self.slf_p)

    def eval_poly_model(self, x):
        if self.log_polypar is None:
            self.fit_lopoly(self.cfg["periodograms"]["polyfit_order"])

        logfreq = np.log10(self.lsfreq)
        logvals = n_model_poly(logfreq, *self.log_polypar)
        return 10**logvals


    def debug_plot(self):
        pl.plot(self.lsfreq, self.lsamp, color="black")
        pl.show()
        pl.clf()
    def peak_selection_debug_plot_slf(self, working_mask):
        pl.plot(self.lsfreq[working_mask], self.lsamp[working_mask], color="green", linestyle="none", marker=".", markersize=2)
        pl.plot(self.lsfreq[~working_mask], self.lsamp[~working_mask], color="black", linestyle = "none", marker=".", markersize=2)
        pl.plot(self.lsfreq, slf_noise(self.lsfreq, *self.slf_p)*3, color="red", linestyle = "--")
        pl.plot(self.lsfreq, slf_noise(self.lsfreq, *self.slf_p), color="red")
        pl.axhline(0)
        pl.xlim(0, 10)
        pl.show()
        pl.clf()





class AverageRadiusTooNarrow(Exception):
    pass

if __name__=="__main__":
    time = np.linspace(0, 100, 100)
    data = np.random.rand(100)