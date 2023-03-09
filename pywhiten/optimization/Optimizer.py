import lmfit as lm
import numpy as np

def constant_function(x, z):
    return z

class Optimizer:
    """
    Handles chi-squared minimization of single-frequency and multi-frequency sinusoidal models.
    """

    sf_func = None
    mf_func = None
    cfg : dict = None
    c_zp : float

    def __init__(self, cfg):
        if type(cfg) == dict:
            self.cfg = cfg

    def single_frequency_opt(self, x, data, err, f0, a0, p0, method="lmfit"):
        initial_guess = [f0, a0, p0]
        if method == "lmfit":
            # this loop exists so that we can check the results and re-run the fit if certain conditions aren't met
            # the only certain condition at the moment is whether the phase value has moved more than 0.1 from its
            # initial guess
            while True:
                """Optimize a single-frequency sinusoidal model using lmfit"""
                sfmod = lm.Model(self.sf_func)
                sfmod.set_param_hint("f", value=f0, min=f0 * self.cfg["autopw"]["bounds"]["freq_lower_coeff"],
                                     max=f0 * self.cfg["autopw"]["bounds"]["freq_upper_coeff"])
                sfmod.set_param_hint("a", value=a0, min=a0 * self.cfg["autopw"]["bounds"]["amp_lower_coeff"],
                                     max=a0 * self.cfg["autopw"]["bounds"]["amp_upper_coeff"])
                sfmod.set_param_hint("p", value=p0, min=self.cfg["autopw"]["bounds"]["phase_lower"],
                                     max=self.cfg["autopw"]["bounds"]["phase_upper"])

                sfmod.print_param_hints()

                f_result = sfmod.fit(data=data, weights=err, x=x)
                # print(f_result.fit_report())

                # if requested, check to see if phase value moved
                if self.cfg["optimization"]["sf_phase_value_check"] and \
                        abs(f_result.best_values["p"] - initial_guess[2]) < 0.1:
                    initial_guess[2] += 0.17
                else:
                    return f_result.best_values["f"], f_result.best_values["a"], \
                        f_result.best_values["p"], f_result.best_fit

    def multi_frequency_optimization(self, x, data, err, freqs):
        """
        Optimize a multi-frequency model (complete variability model) using LMFit
        :param x: The time axis of the original light curve
        :param data: The data axis of the original light curve
        :param err: The uncertainties on the data of the original light curve
        :param freqs: A list of Freq objects passed by reference. These will be updated in-place.
        :param zp: The floating-mean zp from the previous multi-frequency optimization
        :return: A best-fit model evaluated at the input x values, a new optimized floating-mean zp
        """
        sf_mods = []
        for i in range(len(freqs)):
            freq = freqs[i]
            sfmod = lm.Model(self.sf_func)
            sfmod.set_param_hint("f", value=freq.f, min=freq.f * self.cfg["autopw"]["bounds"]["freq_lower_coeff"],
                                 max=freq.f * self.cfg["autopw"]["bounds"]["freq_upper_coeff"])
            sfmod.set_param_hint("a", value=freq.a, min=freq.a * self.cfg["autopw"]["bounds"]["amp_lower_coeff"],
                                 max=freq.a * self.cfg["autopw"]["bounds"]["amp_upper_coeff"])
            sfmod.set_param_hint("p", value=freq.p, min=self.cfg["autopw"]["bounds"]["phase_lower"],
                                 max=self.cfg["autopw"]["bounds"]["phase_upper"])
            sf_mods.append(sfmod)
        zeroptmodel = lm.Model(constant_function, prefix="zp")
        zeroptmodel.set_param_hint(f"zpz", value=self.c_zp)
        if self.cfg["optimization"]["include_zp"]:
            sf_mods.append(zeroptmodel)
        mf_mod = np.sum(sf_mods)
        f_result = mf_mod.fit(data=data, weights=err, x=x)
        # print(f_result.fit_report())

        for i in range(len(freqs)):
            # check boundaries - If any parameters are suspiciously close to a boundary, warn the user
            c_sfmod = sf_mods[i]
            for ptype in ["f", "a", "p"]:
                if abs(c_sfmod.param_hints[ptype]["min"] - f_result.best_values[f"f{i}{ptype}"]) \
                        < self.cfg["optimization"]["mf_boundary_warnings"] * f_result.best_values[f"f{i}{ptype}"]:
                    print(f"\t\t WARNING: {ptype} {f_result.best_values[f'f{i}{ptype}']} of f{i} within"
                          f" {self.cfg['optimization']['mf_boundary_warnings'] * 100}% of lower boundary {c_sfmod.param_hints[ptype]['min']}")
                elif abs(c_sfmod.param_hints[ptype]["max"] - f_result.best_values[f"f{i}{ptype}"]) < \
                        self.cfg['optimization']['mf_boundary_warnings'] * f_result.best_values[f"f{i}{ptype}"]:
                    print(f"\t\t WARNING: {ptype} {f_result.best_values[f'f{i}{ptype}']} of f{i}"
                          f" within {self.cfg['optimization']['mf_boundary_warnings'] * 100}% of upper boundary {c_sfmod.param_hints[ptype]['max']}")
            # update the frequencies in-place
            freqs[i].f = f_result.best_values[f"f{i}f"]
            freqs[i].a = f_result.best_values[f"f{i}a"]
            freqs[i].p = f_result.best_values[f"f{i}p"]
        if self.cfg["optimization"]["include_zp"]:
            print(f"MF ZP: {f_result.best_values['zpz']}")
            self.c_zp = f_result.best_values["zpz"]
        return f_result.best_fit
