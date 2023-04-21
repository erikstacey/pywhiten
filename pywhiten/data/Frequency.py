from typing import Union
from pywhiten.optimization.models import sin_model

class Frequency:
    """
    An object storing a set of parameters for a sinusoidal single-frequency model.
    Attributes:
        f : float
            Model frequency
        sigma_f : float
            frequency uncertainty
        a : float
            Model amplitude
        sigma_a : float
            amplitude uncertainty
        p : float
            Model phase
        sigma_p : float
            phase uncertainty
        t0 : float
            The timestamp which is used as the reference for the measurement of phase. The phase measurement is
            meaningless without this specified.
        sig_poly : float
            Significance as measured using a low-order polynomial fit to the residual light curve's periodogram
        sig_avg : float
            Significance as measured using a rolling box average of the residual light curve's periodogram
        sig_slf : float
            Significance as measured by fitting the Bowman et al. SLF variability model to the residual light curve's
            periodogram

        f0 : float
            The value of f when this object was initialized
        a0 : float
            The value of a when this object was initialized
        p0 : float
            The value of p when this object was initialized

        n: int
            An index label
        model_function : function
            A function of the form f(x, f, a, p) which described the variability model.
    """
    f : float
    sigma_f : float
    a : float
    sigma_a : float
    p : float
    sigma_p : float
    t0 : float
    sig_poly : float
    sig_avg : float
    sig_slf : float
    f0 : float
    a0 : float
    p0 : float

    n = None
    model_function = None

    def __init__(self, f:float, a:float, p:float, t0:float=0, model_function=sin_model, n:Union[int, None]=None):
        """

        Args:
            f (float): initial frequency
            a (float): initial amplitude
            p (float): initial phase
            t0 (float): reference time for phase
            model_function (function reference): A model function. This will typically be the model used to opimize the
                f, a, p parameters. This is required to fully specify the meaning of f, a, p, and t0. Must be of the
                form f(x, f, a, p). Defaults to sin model, as with anything else that utilizes a model of this form.
            n (int): index label
        Returns:
            Nothing
        """
        self.f = f
        self.f0 = f
        self.a = a
        self.a0 = a
        self.p = p
        self.p0 = p
        self.t0 = t0
        self.n = n
        self.model_function = model_function

        self.sig_poly = 0
        self.sig_avg = 0
        self.sig_slf = 0


    def update(self, f, a, p):
        """Updates the stored frequency, amplitude, and phase"""
        self.f, self.a, self.p = f, a, p

    def get_parameters(self):
        """Returns the frequency, amplitude, phase"""
        return self.f, self.a, self.p

    def adjust_params(self):
        """Adjusts amplitude to be positive and phase to be within [0, 1] without changing the model."""
        # adjust amplitude
        if self.a < 0:
            self.a = abs(self.a)
            self.p += 0.5

        if self.p > 1 or self.p < 0:
            self.p = self.p % 1

    def evaluate_model(self, x):
        return self.model_function(x, self.f, self.a, self.p)

    def prettyprint(self):
        """Prints the parameters to console"""
        if self.n is not None:
            print(f"\tf{self.n}: f = {self.f:.5f} | a = {self.a:.3f} | phi = {self.p:.3f}")
        else:
            print(f"\tf(no idx.): f = {self.f:.5f} | a = {self.a:.3f} | phi = {self.p:.3f}")
