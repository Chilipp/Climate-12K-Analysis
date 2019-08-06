# Climate-12K-Analysis
Analysis scripts for Climate-12K

Automated tests are stored in the tests directory. The LiPD data is
stored in the data directory (**not tracked by git**).

To download the LiPD files and combine the temperature series, run the
[get-temperature-data.ipynb](get-temperature-data.ipynb) jupyter notebook
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

## Running the tests
Then download the LiPD database from http://lipdverse.org/globalHolocene/current_version,
e.g. http://lipdverse.org/globalHolocene/current_version/globalHolocene0_30_1.zip
and unzip this file to the `data` directory.

Finally, run the tests via

```bash
pytest tests
```

This will generate an Excel file in `data/results.xlsx` with a summary of the
tests. Additionally, you can pass the `--html` option to create a nice looking
html report:

```bash
pytest tests --html=data/report.html
```

These commands run a lot of tests for the invidual time series and you
can review the outcome in `data/results.xlsx` and `data/report.html`. You can
also specify a directory different from `data` with the `--lipd-data` option,
e.g.

```bash
pytest tests --lipd-data=another-data-directory
```

`pytest` has a lot of options to select specific tests, e.g. through the `-k`
option. Please use `pytest -h` to see the available options.


### Accepting test failures
If you  decide, that one test outcome should be accepted and not marked as
failed, add it's nodeid to a file and pass it to the `pytest` command via the
`--accepted` option.

Imagine the country test (`test_country`) failed for the `LPDd2a984fe`
time series in the `AMP112.vanderBilt.2016.lpd` dataset. To accept this
failure, follow these steps:

1. Look for the `nodeid-tests/test_data.py::test_country` column in
   `data/results.xlsx`
2. Get down to the row for `AMP112.vanderBilt.2016` and `LPDd2a984fe`
3. copy the cell in this column (in our case,
   `tests/test_data.py::test_country[AMP112.vanderBilt.2016.LPDd2a984fe]`) and
	paste that into a text file, e.g. `data/accepted.txt`.
4. Run the tests again while specifying the text file for the `--accepted`
   option via

   ```bash
   pytest tests --accepted=data/accepted.txt
   ```

You can add as many lines (i.e. test nodeids) to this file as you like.


## Running jupyter notebooks
With the activated conda environment (see above), you should install the
ipython kernel via

```bash
python -m ipykernel install --user
```

to make sure that the notebook server uses the correct environment.

Then start the notebook server via

```bash
jupyter notebook
```

which will open your browser and let you run the corresponding notebook.
