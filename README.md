# Climate-12K-Analysis
Analysis scripts for Climate-12K

Automated tests are stored in the tests directory. The LiPD data is
stored in the data directory (**not tracked by git**).

To download the LiPD files, run [get-temperature-data.ipynb](get-temperature-data.ipynb)
(see also the installation instructions below).

## Installation
After having installed [miniconda](https://conda.io/en/latest/miniconda.html),
create a new environment using the [environment.yml](environment.yml)
configuration file:

```bash
conda env create -f environment.yml
```

and activate it via

```bash
conda activate climate12k
```

Then you should also install the ipython kernel via

```bash
python -m ipykernel install --user
```

to make sure that the notebook server uses the correct environment.

## How to run these scripts locally

Start a notebook server via

```bash
jupyter notebook
```

Run the [get-temperature-data.ipynb](get-temperature-data.ipynb) notebook with
the necessary configuration and afterwards you can test the downloaded data via

```bash
pytest tests
```
