import os
import shutil
import numpy as np

import matplotlib.pyplot as pl
from pywhiten.pwio.utilities import flux2mag, flux2mag_e, format_output

class OutputManager:
    """
    Handles saving results and auxiliary data.
    """

    """
        Handles output data/plots and associated formatting for lightcurves, periodograms, and other data from the
        pre-whitening analysis.
        Attributes:
            np.array model_x: An x-array used to make models of variability models, such that they can be plotted over LCs
            
            dict output_dirs: A dictionary of output directories, containing the following keyed values:
                string main_dir: The absolute path to the main output directory
                string pgs_output: The absolute path to the subdirectory where all periododgram data/plots are saved
                string pgs_slf_output: The absolute path to the subdirectory where periodograms are saved with slf fits overlaid
                string pgs_box_avg_output: "" box average profiles overlaid - Currently nothing is saved here
                string pgs_lopoly_output: "" Low-order polynomial fits overlaid, only the final periodogram is currently saved
                string pgs_data_output: The absolute path to the subdirectory where the raw data of each periodogram is saved
                string lcs_output: The absolute path to the subdirectory where all light curve data/plots are saved
                string lcs_sf_output: The absolute path to the subdirectory where light curve plots are saved with single-freq
                    variability models overlaid
                string lcs_mf_output: The absolute path to the subdirectory where light curves are saved with complete
                    variability models overplotted
                string lcs_data_output: The absolute path to the subdirectory where the raw data of residual light curves are
                    saved
                string misc_output: The absolute path where misc data and plots are saved
        """
    model_x : np.ndarray
    cfg : dict

    output_dirs = {"base": None,
                   "pgs_base": None,
                   "pgs_raw": None,
                   "pgs_slf": None,
                   "pgs_box": None,
                   "pgs_lopoly": None,
                   "lcs_base": None,
                   "lcs_raw": None,
                   "lcs_sf": None,
                   "lcs_mf": None,
                   "lcs_data": None,
                   "auxiliary":None}

    def __init__(self, cfg):
        # Make directories
        try:
            # set up base directory
            if cfg["output"]["paths"]["base"] in [".", "cwd", "/."]:
                self.output_dirs["base"] = os.getcwd()
            else:
                self.output_dirs["base"] = os.getcwd() + cfg["output"]["paths"]["base"]
            # set up second level directories
            for key in ["pgs_base", "lcs_base", "auxiliary"]:
                self.output_dirs[key] = self.output_dirs["base"] + cfg["output"]["paths"][key]
            # set up pgs directories
            for key in ["pgs_raw", "pgs_slf", "pgs_box", "pgs_lopoly"]:
                self.output_dirs[key] = self.output_dirs["pgs_base"] + cfg["output"]["paths"][key]
            # set up lcs directories
            for key in ["lcs_raw", "lcs_sf", "lcs_mf", "lcs_data"]:
                self.output_dirs[key] = self.output_dirs["lcs_base"] + cfg["output"]["paths"][key]
        except KeyError:
            raise KeyError("Issue with specified output directories")

        if os.path.exists(self.output_dirs["base"]):
            shutil.rmtree(self.output_dirs["base"])

        # now actually make the directories
        for path_key in self.output_dirs:
            os.makedirs(self.output_dirs[path_key], exist_ok = True)









