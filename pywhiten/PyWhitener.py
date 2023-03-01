import tomli
from pywhiten.data import *
from pywhiten.pwio import OutputManager
import os
import numpy as np

class PyWhitener:
    """
    The main object used to conduct pre-whitening analyses.
    """
    lcs: list
    freqs: FrequencyContainer
    cfg: dict
    output_manager : OutputManager


    def __init__(self, time, data, err=None, cfg_file = "default", cfg = None):

        # using this method to load the cfg maintains backwards compatibility with python 3.7 in the least painful form
        # load default cfg, then overwrite with config file specified by cfg
        pkg_path = os.path.abspath(__file__)[:-14]
        default_config = pkg_path +"/cfg/default.toml"
        with open(default_config, "rb") as f:
            self.cfg = tomli.load(f)

        if cfg_file != "default" and type(cfg_file) == str:
            # if specified cfg file is in current directory, use that
            if os.path.exists(f"{os.getcwd()}/+{cfg_file}"):
                with open(f"{os.getcwd()}/+{cfg_file}", "rb") as f:
                    loaded_cfg = tomli.load(f)
                    self.cfg = merge_dict(self.cfg, loaded_cfg)
            # try to find it in the cfg directory instead
            elif os.path.exists(f"{pkg_path}/cfg/{cfg_file}"):
                with open(f"{pkg_path}/cfg/{cfg_file}", "rb") as f:
                    loaded_cfg = tomli.load(f)
                    self.cfg = merge_dict(self.cfg, loaded_cfg)
            # finally, check to see if the cfg file was specified as a full path
            elif os.path.exists(cfg_file):
                with open(cfg_file, "rb") as f:
                    loaded_cfg = tomli.load(f)
                    self.cfg = merge_dict(self.cfg, loaded_cfg)
        # use the cfg argument of the initializer to overwrite any cfg entries
        if cfg is not None and type(cfg) == dict:
            self.cfg = self.cfg = merge_dict(self.cfg, cfg)
        # config setup done
        # now set up initial light curve, frequency container, output mgr
        self.lcs = [Lightcurve(time, data, err)]
        self.freqs = FrequencyContainer()
        self.output_manager = OutputManager(cfg = self.cfg)

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
