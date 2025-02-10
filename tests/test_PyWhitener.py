import numpy as np
import pywhiten
def test_PyWhitener():
    x = np.linspace(0, 100, 10000)
    y = np.zeros(10000)

    y += 10*np.sin(2*np.pi*(1.25*x+0.25))
    y += 5 * np.sin(2 * np.pi * (3.15 * x + 0.7))
    y += 2 * np.sin(2 * np.pi * (5.4 * x + 0.9))

    errors = np.random.rand(10000)

    test_PyWhitener = pywhiten.PyWhitener(x, y, errors)

    test_PyWhitener.it_pw()
    test_PyWhitener.it_pw_manual(5.4, 2, 0.9)
    test_PyWhitener.it_pw()

