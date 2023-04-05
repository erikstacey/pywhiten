import pywhiten
import numpy as np
from pywhiten.data import Lightcurve

def test_FrequencyContainer_basic_functionality():
    f1 = pywhiten.data.Frequency(1.0, 2.0, 3.0, t0=0, n=0)
    f2 = pywhiten.data.Frequency(2.2, 2.3, 4.1, t0=0, n=1)
    f3 = pywhiten.data.Frequency(0.1, 20, 0.3, t0=0, n=2)

    test_container = pywhiten.data.FrequencyContainer(f1, f2)
    assert len(test_container.get_flist()) == 2
    assert test_container.get_last_frequency().f == 2.2
    test_container.add_frequency(f3)
    assert len(test_container.get_flist()) == 3
    assert test_container.get_last_frequency().f == 0.1

    test_model = test_container.mf_model(np.linspace(0, 10, 100), 0)
    assert np.all(test_model == pywhiten.optimization.n_sin_model(np.linspace(0, 10, 100),
                                                            1.0, 2.2, 0.1,
                                                            2.0, 2.3, 20,
                                                            3.0, 4.1, 0.3,
                                                            0))

def test_FrequencyContainer_significances_and_uncertainties():
    f1 = pywhiten.data.Frequency(1.0, 2.0, 3.0, t0=0, n=0)
    f2 = pywhiten.data.Frequency(2.2, 2.3, 4.1, t0=0, n=1)
    f3 = pywhiten.data.Frequency(0.1, 20, 0.3, t0=0, n=2)

    test_container = pywhiten.data.FrequencyContainer(f1, f2, f3)

    test_lc_time = np.linspace(0, 10, 1000)
    test_lc_data = (np.random.rand(1000)-0.5) * 20
    for i in range(1, 1000):
        test_lc_data[i] += test_lc_data[i-1]*0.95


    test_lc = Lightcurve(test_lc_time, test_lc_data-np.mean(test_lc_data), np.ones(1000))

    test_container.compute_parameter_uncertainties(test_lc)
    test_container.compute_significances(test_lc.periodogram)

    for i in range(len(test_container.get_flist())):
        assert test_container.get_flist()[i].sig_slf is not None
        assert test_container.get_flist()[i].sig_box is not None
        assert test_container.get_flist()[i].sig_poly is not None
        assert test_container.get_flist()[i].sigma_f is not None
        assert test_container.get_flist()[i].sigma_a is not None
        assert test_container.get_flist()[i].sigma_p is not None

