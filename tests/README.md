# Testing the Temperature12K database

## Running the tests
You can either run the tests online on a remote server with mybinder.org

https://mybinder.org/v2/gh/Chilipp/Temperature12K-Analysis/master?filepath=notebooks/run-temperature12k-tests.ipynb

or on your local machine. For the latter, make sure you followed the
[installation instructions for this repository](../README.md#installation).

Then download the LiPD database from http://lipdverse.org/globalHolocene/current_version,
e.g. http://lipdverse.org/globalHolocene/0_30_1/globalHolocene0_30_1.zip
and unzip this file to the `../data` directory.

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


## Accepting test failures
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


## Adding new tests
We very much welcome tests for the Temperature12K database! Please head over to our
[contributing guide](../CONTRIBUTING.md#adding-new-tests) to learn more about
the test framework.
