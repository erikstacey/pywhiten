import os
import tomli
import numpy as np
from pywhiten.optimization.Optimizer import Optimizer
from pywhiten.optimization.models import sin_model, n_sin_model
from pywhiten.data.Frequency import Frequency
from pywhiten.data.FrequencyContainer import FrequencyContainer

def test_sin_model():
    test_x = np.linspace(0, 10, 1000)
    test_y = sin_model(test_x, 1.0, 10, 0.5)
    assert round(test_y[0], 5) == 0.00000

def test_Optimizer_sf():
    default_config = os.getcwd()+"/pywhiten/cfg/default.toml"
    with open(default_config, "rb") as f:
        cfg = tomli.load(f)

    test_Optimizer = Optimizer(cfg=cfg)

    assert test_Optimizer.sf_func == sin_model
    assert test_Optimizer.mf_func == n_sin_model
    assert test_Optimizer.c_zp == 0

    test_x = np.linspace(0, 10, 1000)
    test_y = sin_model(test_x, 1.0, 10, 0.5)

    fit_f, fit_a, fit_p, model = test_Optimizer.single_frequency_optimization(test_x, test_y, np.ones(len(test_x)), 1.5, 8, 0)

def test_Optimizer_mf():
    default_config = os.getcwd()+"/pywhiten/cfg/default.toml"
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
    assert test_container.get_flist()[0].f == 1.1
    model = test_Optimizer.multi_frequency_optimization(test_x, test_y, np.ones(len(test_x)),
                                                        test_container.get_flist())
    assert test_container.get_flist()[0].f != 1.1