from setuptools import setup

setup(name="pywhiten",
      version="1.0.3",
      description="A python package for conducting Lomb-Scargle-based prewhitening of stellar time series. ",
      url="https://www.github.com/erikstacey/pywhiten",
      author="Erik William Stacey",
      author_email = "erik@erikstacey.com",
      license="MIT",
      packages=["pywhiten"],
      install_requires=[
            "numpy",
            "matplotlib",
            "scipy",
            "astropy",
            "lmfit",
            "tomli"
      ],
      tests_require=["pytest"],
      zip_safe = False,
      include_package_data=True,
      package_data={'': ['/cfg/default.toml']},
      )