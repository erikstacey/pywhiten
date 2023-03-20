import lmfit as lm
import numpy as np
from pywhiten.optimization.models import sin_model, n_sin_model, cos_model, n_cos_model

def constant_function(x, z):
    return z

class Optimizer:
    """
    Handles chi-squared minimization of single-frequency and multi-frequency sinusoidal models.
    Attributes:
        sf_func (Function): A sinusoidal function taking arguments of the format x:ndarray, f:float, a:float, p:float
            used for single-frequency optimizations and summed for multi-frequency optimizations when using lmfit as the
            optimization engine
        mf_func (Function): A function taking arguments of the format x:ndarray, *pars, where *pars is an arbitrarily
            large set of floats arranged such that it contains a group of frequency guesses followed by a group of
            amplitude guesses followed by a group of phase guesses followed by a guess for the zero point. The
            frequency, amplitude, and phase guesses must be of equal size, meaning *pars should be of length 3n+1 where
            n is some positie integer
        cfg (dict): A configuration dictionary. See pywhitener.cfg for further details.
        c_zp (float): A guess for the zero point used when performing multi-frequency fits. This is stored as an
            attribute so it can be refined over multiple multi-frequency fits as frequencies are added
    """

    sf_func = None
    mf_func = None
    cfg : dict = None
    c_zp : float = 0

    def __init__(self, cfg):
        if type(cfg) == dict:
            self.cfg = cfg

        # set up optimization functions
        if self.cfg["optimization"]["frequency_model_type"] == "sin":
            self.sf_func = sin_model
            self.mf_func = n_sin_model
        elif self.cfg["optimization"]["frequency_model_type"] == "cos":
            self.sf_func = cos_model
            self.mf_func = n_cos_model
        else:
            raise ValueError(f"Configuration optimization.frequency_model_type is set to"
                             f" {self.cfg['optimization']['frequency_model_type']}, must be 'sin' or 'cos'")

        self.c_zp = 0
    def single_frequency_optimization(self, x, data, err, f0, a0, p0, method="lmfit"):
        """
        Optimizes a single sinusoidal model to an x-y dataset
        Args:
            x (ndarray): x values of data to fit to
            data (ndarray): y values of data to fit to
            err (ndarray): data point weights
            f0 (float): guess for frequency
            a0 (float): guess for amplitude
            p0 (float): guess for phase
            method (str): can be one of "lmfit" or "scipy", and defines the package to use to conduct the minimization
                scipy directly implements MINPACK fortran routines, whereas lmfit implements additional functionality
                to handle parameter boundaries with more grace. Only lmfit works right now

        Returns:

        """
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


                f_result = sfmod.fit(data=data, weights=err, x=x)

                # if requested, check to see if phase value moved
                if self.cfg["optimization"]["sf_phase_value_check"] and \
                        abs(f_result.best_values["p"] - initial_guess[2]) < 0.1:
                    initial_guess[2] += 0.17
                else:
                    return f_result.best_values["f"], f_result.best_values["a"], \
                        f_result.best_values["p"], f_result.best_fit

    def multi_frequency_optimization(self, x, data, err, freqs):
        """
        Optimizes a multi-frequency model composed of sinusoidal components against an x-y dataset.
        Args:
            x (ndarray): x values of data to fit to
            data (ndarray): y values of data to fit to
            err (ndarray): data weights
            freqs(list): A list of one or more Frequency objects, where the Frequency
                objects f, a, and p attributes are used as initial guesses for the frequencies, amplitudes, and phases,
                and the these values are updated in-place after the optimization is complete (only an evaluated model
                is returned)

        Returns:
            ndarray: the optimized multi-frequency model evaluated at all values of x
        """
        sf_mods = []
        for i in range(len(freqs)):
            freq = freqs[i]
            sfmod = lm.Model(self.sf_func, prefix=f"f{i}")
            sfmod.set_param_hint(f"f{i}f", value=freq.f, min=freq.f * self.cfg["autopw"]["bounds"]["freq_lower_coeff"],
                                 max=freq.f * self.cfg["autopw"]["bounds"]["freq_upper_coeff"])
            sfmod.set_param_hint(f"f{i}a", value=freq.a, min=freq.a * self.cfg["autopw"]["bounds"]["amp_lower_coeff"],
                                 max=freq.a * self.cfg["autopw"]["bounds"]["amp_upper_coeff"])
            sfmod.set_param_hint(f"f{i}p", value=freq.p, min=self.cfg["autopw"]["bounds"]["phase_lower"],
                                 max=self.cfg["autopw"]["bounds"]["phase_upper"])
            sf_mods.append(sfmod)
        zeroptmodel = lm.Model(constant_function, prefix="zp")
        zeroptmodel.set_param_hint(f"zpz", value=self.c_zp)
        if self.cfg["optimization"]["mf_include_zp"]:
            sf_mods.append(zeroptmodel)
        mf_mod = np.sum(sf_mods)
        f_result = mf_mod.fit(data=data, weights=err, x=x)
        # print(f_result.fit_report())

        for i in range(len(freqs)):
            # check boundaries - If any parameters are suspiciously close to a boundary, warn the user
            c_sfmod = sf_mods[i]
            if self.cfg["optimization"]["mf_boundary_warnings"] != 0:
                for ptype in ["f", "a", "p"]:
                    if abs(c_sfmod.param_hints[ptype]["min"] - f_result.best_values[f"f{i}{ptype}"]) \
                            < self.cfg["optimization"]["mf_boundary_warnings"] * f_result.best_values[f"f{i}{ptype}"]:
                        print(f"\t\t WARNING: {ptype} {f_result.best_values[f'f{i}{ptype}']} of f{i} within"
                              f" {self.cfg['optimization']['mf_boundary_warnings'] * 100}% "
                              f"of lower boundary {c_sfmod.param_hints[ptype]['min']}")
                    elif abs(c_sfmod.param_hints[ptype]["max"] - f_result.best_values[f"f{i}{ptype}"]) < \
                            self.cfg['optimization']['mf_boundary_warnings'] * f_result.best_values[f"f{i}{ptype}"]:
                        print(f"\t\t WARNING: {ptype} {f_result.best_values[f'f{i}{ptype}']} of f{i}"
                              f" within {self.cfg['optimization']['mf_boundary_warnings'] * 100}% "
                              f"of upper boundary {c_sfmod.param_hints[ptype]['max']}")
            # update the frequencies in-place
            freqs[i].f = f_result.best_values[f"f{i}f"]
            freqs[i].a = f_result.best_values[f"f{i}a"]
            freqs[i].p = f_result.best_values[f"f{i}p"]
        if self.cfg["optimization"]["mf_include_zp"]:
            if self.cfg["output"]["print_runtime_messages"]:
                print(f"\tMF ZP: {f_result.best_values['zpz']}")
            self.c_zp = f_result.best_values["zpz"]
        return f_result.best_fit



if __name__ == "__main__":
    import os
    import tomli
    from pywhiten.data import Frequency, FrequencyContainer
    default_config = os.getcwd().strip("optimization") + "cfg/default.toml"
    with open(default_config, "rb") as f:
        cfg = tomli.load(f)

    test_Optimizer = Optimizer(cfg=cfg)

    assert test_Optimizer.sf_func == sin_model
    assert test_Optimizer.mf_func == n_sin_model
    assert test_Optimizer.c_zp == 0

    test_x = np.linspace(0, 10, 1000)
    test_y = sin_model(test_x, 1.0, 10, 0.5) + sin_model(test_x, 1.4, 7, 0.4)

    f1 = Frequency(1.1, 9.0, 0.7, t0=0, n=0)
    f2 = Frequency(1.6, 8.1, 0.8, t0=0, n=1)

    test_container = FrequencyContainer(f1, f2)
    model = test_Optimizer.multi_frequency_optimization(test_x, test_y, np.ones(len(test_x)), test_container)