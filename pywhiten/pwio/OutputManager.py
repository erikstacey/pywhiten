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
            float rflux: The reference flux which was subtracted from the original light curve to yield a differential light
                curve. This is necessary to make proper conversions to magnitude.
            np.array model_x: An x-array used to make models of variability models, such that they can be plotted over LCs
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
    rflux: float = None
    model_x = None

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
            pass
        except KeyError:
            pass





