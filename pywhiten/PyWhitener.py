import tomli
from pywhiten.data import *
import os
import numpy as np

class PyWhitener:
    """
    The main object used to conduct pre-whitening analyses.
    """
    lcs: list
    freqs: FrequencyContainer
    cfg: dict


    def __init__(self, time, data, err=None, cfg = "default"):

        # using this method to load the cfg maintains backwards compatibility with python 3.7 in the least painful form
        # load default cfg, then overwrite with config file specified by cfg
        pkg_path = os.path.abspath(__file__)[:-14]
        default_config = pkg_path +"/cfg/default.toml"
        with open(default_config, "rb") as f:
            self.cfg = tomli.load(f)

        if cfg != "default":
            pass

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
    test_dict = {
        "flt": 1.0,
        "lst": [0, 1, 2],
        "tup": (0, 1, 2),
        "dct": {
            "nested_flt": 1.1,
            "nested_str": "helloworld",
            "nested_dct": {
                "par1": 1.2
            }
        }
    }

    test_dict_2 = {
        "flt": 1.1,
        "lst": [0, 1, 3],
        "tup": (0, 1, 2),
        "dct": {
            "nested_str": "goodbyeworld",
            "nested_dct": {
                "par1": 1.3
            }
        }
    }
    print(merge_dict(test_dict, test_dict_2))
