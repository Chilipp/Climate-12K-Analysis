# Climate-12K-Analysis
Analysis scripts for Climate-12K

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Chilipp/Climate-12K-Analysis/master)

This repository contains an automated test suite for the Climate12K database
and several other analysis notebooks. You can run the analysis scripts in this
repository on a remote server using mybinder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Chilipp/Climate-12K-Analysis/master)

without the need to install anything. Just head over to

https://mybinder.org/v2/gh/Chilipp/Climate-12K-Analysis/master

The following sections describe the other contents of this repository.


## Installation
*Skip this section, if you want to use mybinder.org anyway...*

If you want to run the functionalities in this repository on your local
computer,  you have to install the necessary dependencies as described in the
following steps:

1. Download this repository
2. Download and install [miniconda](https://conda.io/en/latest/miniconda.html)
   for your specific operating system (Linux, Windows or OS X)
3. Create a new conda environment using the [environment.yml](environment.yml)
   configuration file:

   ```bash
   conda env create -f environment.yml
   ```
4. Activate the conda environment via
   ```bash
   conda activate climate12k
   ```

Further installation instructions to run the notebooks can be found
in the corresponding [README](notebooks/README.md).

## Running jupyter notebooks

You can run the notebooks on a remote server (without the need of installing
any packages), or offline. Please head over to the
[notebooks directory][notebooks] for more information on this.

The notebooks in this repository are:

- [get-temperature-data.ipynb](notebooks/get-temperature-data.ipynb) to
  download the LiPD files and combine the temperature series in the data base
- [run-climate12k-tests.ipynb](notebooks/run-climate12k-tests.ipynb) to run
  the automated tests for the database


## Running the tests
Automated tests are defined in the [tests](tests) directory. You can
run these tests with the [run-climate12k-tests.ipynb](notebooks/run-climate12k-tests.ipynb)
or by following the [instructions to run the tests](tests/README.md).


## Contributing and giving feedback

We very much welcome your contributions and appreciate any feedback on the
analysis scripts and tests. Please head over to the
[contributing guide](CONTRIBUTING.md) and let us know your feedback throug
a new [issue](https://github.com/Chilipp/Climate-12K-Analysis/issues) or
via mail to [philipp.sommer@unil.ch](mailto:philipp.sommer@unil.ch).
