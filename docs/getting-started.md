# Installation

pywhiten is available through pip:  
```
pip install pywhiten
```
Or, alternatively, download and install directly from this repo:  
```
git clone https://github.com/erikstacey/pywhiten.git ./pywhiten
cd pywhiten
pip install .
```

## Setting up a tutorial directory
First, lets create a tutorial directory somewhere:
```
mkdir pywhiten_tutorial
cd pywhiten_tutorial
```

Then, grab an example set of time series data [here](https://github.com/erikstacey/pywhiten/blob/master/Sample_Prewhitening_Directory/HD47129_thresh9_lc.txt) and
place it in a tutorial directory. Alternatively, you can provide your own time series data noting that the import examples may differ depending on your data format.
## Importing data and setting up a Pywhitener
To start pre-whitening, we need to load our time series data. But first, we need to create a python script. Here's an example with Vim, however you can use whatever you usually use to write python code:
```
vim example.py
```
Now, writing in our example script, we'll load our time series data into three arrays from the example file:
```
import numpy as np

time, data, err = np.loadtxt("HD47129_thresh9_lc.txt", unpack=True)
```

The Pywhitener class provides an easy-to-use interface to the rest of the package and powerful functionality for automated or semi-automated frequency analysis. Lets make one here by passing in the time series data we just loaded in:

```
pywhitener = pywhiten.PyWhitener(time=time, data=data, err=err)
```

Note that if you don't provide an error array, it will assume the data to be equally weighted. 

## Automatic Pre-Whitening

Now, running an automatic frequency analysis is as simple as calling the auto method:
```
pywhitener.auto()
```

This will automatically proceed through several iterations and, if using the sample data, will terminate after the 16th iteration after achieving the termination criterion. This will also
create a pw_out directory in the working directory and populate it with results. If you want to have a quick peek at the results, have a look at pw_out/frequencies.csv in your shell:
```
more ./pw_out/frequencies.csv
```

## Semi-automatic Pre-Whitening
If you want to proceed in single iterations only, you can do that with the it_pw() method of the pywhitener. Here's an example:

```
import numpy

time, data, err = np.loadtxt("HD47129_thresh9_lc.txt", unpack=True)
pywhitener = pywhiten.PyWhitener(time=time, data=data, err=err)
pywhitener.it_pw()
```
This will identify a single frequency. You can run this ten times to get ten frequencies:
```
for i in range(10):
   pywhitener.it_pw()
```

Or, if you'd like, you can manually specify the frequency/amplitude/phase hints. This will obviously skip the peak selection phase:
```
pywhitener.it_pw_manual(frequency = 0.5, amplitude = 12.5, phase = 0.2)
```


You can output this data to the pw_out directory using
```
pywhitener.post_pw()
```
Now, this example has so far used the default configuration for the program. Pywhiten derives its flexibility from its
configuration files, which make it possible to automate batch running frequency analyses on data from different instruments
with different configuration requirements. More details on the configuration can be found [here](https://pywhiten.readthedocs.io/en/latest/configuration)

## Directly Accessing Data and Results

If you'd like to directly access the results, that's easily accomplished through the attributes of the pywhitener.

### Light Curves

Light curves are stored in a list in the lcs attribute. Here's an example of accessing the residual lightcurve of the last iteration and plotting the results:
```
import matplotlib.pyplot as pl
residual_lc = pywhitener.lcs[-1]
pl.plot(residual_lc.time, residual_lc.data)
pl.show()
```
Refer to the documentation for what can be achieved using the Lightcurve objects.

### Periodograms

As periodograms are a description of the frequency spectrum of a time series, they are stored within the Lightcurve objects. Here's an example of accessing and plotting the residual periodogram:
```
import matplotlib.pyplot as pl
residual_lc = pywhitener.lcs[-1]
residual_periodogram = residual_lc.periodogram
pl.plot(residual_periodogram.lsfreq, residual_periodogram.lsamp)
pl.show()
```

### Frequencies

Unlike light curves, Frequency objects are stored in their own special container. A list of frequency objects can be acquired through a method of the FrequencyContainer object:
```
frequencies_list = pywhitener.freqs.get_flist()
print(f"The last identified frequency is at {frequencies_list[-1].f:.5f} with an amplitude of {frequencies_list[-1].a:.5f}!)
```

All of the Frequency, FrequencyContainer, Lightcurve, and Periodogram objects have useful functionality which is documented in the Data module of the docs!