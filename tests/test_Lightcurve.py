import pywhiten
import numpy as np
def test_Lightcurve():
    test_Lightcurve = pywhiten.data.Lightcurve(np.linspace(0, 30, 14000),
                                               np.random.random(14000), err = np.random.random(14000))

