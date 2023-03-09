import tomli
from pywhiten.data import *
from pywhiten.pwio import OutputManager
from pywhiten.optimization.Optimizer import Optimizer
import os
import numpy as np


class PyWhitener:
    """
    The main object used to conduct pre-whitening analyses.
    Attributes:
        list lcs
    """
    lcs: list
    freqs: FrequencyContainer
    cfg: dict
    output_manager: OutputManager
    optimizer: Optimizer

    def __init__(self, time, data, err=None, cfg_file="default", cfg=None):

        # using this method to load the cfg maintains backwards compatibility with python 3.7 in the least painful form
        # load default cfg, then overwrite with config file specified by cfg
        pkg_path = os.path.abspath(__file__)[:-14]
        default_config = pkg_path + "/cfg/default.toml"
        with open(default_config, "rb") as f:
            self.cfg = tomli.load(f)

        if cfg_file != "default" and type(cfg_file) == str:
            # if specified cfg file is in current directory, use that
            if os.path.exists(f"{os.getcwd()}/+{cfg_file}"):
                with open(f"{os.getcwd()}/+{cfg_file}", "rb") as f:
                    loaded_cfg = tomli.load(f)
                    self.cfg = merge_dict(self.cfg, loaded_cfg)
                self.cfg["title"] = "Config loaded from file in working directory"
            # try to find it in the cfg directory instead
            elif os.path.exists(f"{pkg_path}/cfg/{cfg_file}"):
                with open(f"{pkg_path}/cfg/{cfg_file}", "rb") as f:
                    loaded_cfg = tomli.load(f)
                    self.cfg = merge_dict(self.cfg, loaded_cfg)
                self.cfg["title"] = "Config loaded from file in package cfg directory"
            # finally, check to see if the cfg file was specified as a full path
            elif os.path.exists(cfg_file):
                with open(cfg_file, "rb") as f:
                    loaded_cfg = tomli.load(f)
                    self.cfg = merge_dict(self.cfg, loaded_cfg)
                self.cfg["title"] = "Config loaded from file at specified path"
        # use the cfg argument of the initializer to overwrite any cfg entries
        if cfg is not None and type(cfg) == dict:
            self.cfg = self.cfg = merge_dict(self.cfg, cfg)
            self.cfg["title"] += " - Merged with runtime-specified arguments"
        # handle special logic cases
        pass
        # config setup done
        # now set up initial light curve, frequency container, output mgr
        self.lcs = [Lightcurve(time, data, err)]
        self.freqs = FrequencyContainer()
        self.output_manager = OutputManager(cfg=self.cfg)
        self.optimizer = Optimizer()

        # we're now ready to do some frequency analysis

    def id_peak(self, method, idx=-1):
        return self.lcs[idx].periodogram.select_peak(method=method,
                                                     min_prov_sig=self.cfg["autopw"]["peak_selection_cutoff_sig"])

    def it_pw(self, peak_selection_method="highest"):
        """
        Conducts a single pre-whitening iteration. Identifies a candidate frequency/amplitude from the most recent
        light curve, fits a single-frequency sinusoid to the most recent light curve and includes it as a frequency,
        improves all parameters of all frequencies in multi-frequency fit against original light curve, and makes a new
        light curve ready for another iteration.
        Args:
            peak_selection_method (str):  the peak selection method used to get a candidate frequency/amplitude. can be
                one of ['highest', 'slf', 'poly', 'avg'] - see id_peak method of data.Periodogram class

        Returns:
            bool: indicates pre-whitening iteration success
        """
        if self.cfg["output"]["print_runtime_messages"]:
            print(f"[pywhiten] ITERATION {self.freqs.n + 1}")

        # First stage, identify a candidate frequency/amplitude from the most recent periodogram
        candidate_frequency, candidate_amplitude = self.id_peak(method=peak_selection_method)

        # Second stage, conduct a single-frequency fit
        sf_f, sf_a, sf_p, sf_model = self.optimizer.single_frequency_opt(self.lcs[-1].time,
                                                                         self.lcs[-1].data,
                                                                         self.lcs[-1].err,
                                                                         candidate_frequency, candidate_amplitude, 0.5)
        self.freqs.add_frequency(Frequency(f=sf_f, a=sf_a, p=sf_p, t0=self.cfg["input"]["input_t0"]))

        # Third stage, conduct the multi-frequency fit
        mf_mod = self.optimizer.multi_frequency_optimization(self.lcs[0].time,
                                                             self.lcs[0].data,
                                                             self.lcs[0].err,
                                                             self.freqs.get_flist())

        # %todo: Populate the OutputManager with iteration saving functionality and put a "save iteration" here

        # Final Stage, make a new light curve and append it to the lightcurves list
        if self.cfg["autopw"]["new_lc_generation_method"] == "mf":
            self.lcs.append(Lightcurve(self.lcs[0].time, self.lcs[0].data - mf_mod, err = self.lcs[0].err))
            return True
        elif self.cfg["autopw"]["new_lc_generation_method"] == "sf":
            self.lcs.append(Lightcurve(self.lcs[-1].time, self.lcs[-1].data - sf_model, err=self.lcs[0].err))
            return True
        return False



def merge_dict(old_dict, new_dict):
    out_dict = {}
    for key in new_dict.keys():
        if key in old_dict.keys() and type(old_dict[key]) == dict:
            out_dict[key] = merge_dict(old_dict[key], new_dict[key])
        else:
            out_dict[key] = new_dict[key]
    for key in old_dict.keys():
        if key not in out_dict.keys():
            out_dict[key] = old_dict[key]
    return out_dict


if __name__ == "__main__":
    test_pywhitener = PyWhitener(np.linspace(0, 10, 100), np.random.rand(100), np.ones(100))
    print(test_pywhitener.cfg)
