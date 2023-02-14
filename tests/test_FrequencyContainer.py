import pywhiten
import numpy as np

def test_FrequencyContainer():
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