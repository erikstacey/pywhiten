import pywhiten
import numpy as np

def test_autoPreWhitener():
    time, data, err = np.loadtxt("HD47129_thresh9_lc.txt", unpack=True)
    pywhitener = pywhiten.PyWhitener(time=time, data=data, err=err)

    pywhitener.auto()

test_autoPreWhitener()