

class Frequency:
    """
    An object storing a set of parameters for a sinusoidal single-frequency model.
    Attributes:
        f : float
            Model frequency
        a : float
            Model amplitude
        p : float
            Model phase
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
    """
    def __init__(self, f, a, p, t0, n=None):
        self.f = f
        self.f0 = f
        self.a = a
        self.a0 = a
        self.p = p
        self.p0 = p
        self.t0 = t0
        self.n = n

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

    def prettyprint(self):
        """Prints the parameters to console"""
        if self.n is not None:
            print(f"\tf{self.n}: f = {self.f:.5f} | a = {self.a:.3f} | phi = {self.p:.3f}")
        else:
            print(f"\tf(no idx.): f = {self.f:.5f} | a = {self.a:.3f} | phi = {self.p:.3f}")