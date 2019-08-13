# How to contribute to this repository

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

We very much welcome new contributions through analysis notebooks or new tests for the database!

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Pull Requests](#pull-requests)
  * [Adding new tests](#adding-new-tests)
  * [Adding new analysis notebooks](#adding-new-analysis-notebooks)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Documentation Styleguide](#documentation-styleguide)


## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

### Reporting Bugs

This section guides you through submitting a bug report for this repository. Following these guidelines helps
maintainers and the community understand your report, reproduce the behavior, and find related reports.

Before creating bug reports, please check existing issues and pull requests as you might find out that
you don't need to create one. When you are creating a bug report, please include as many details as possible.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing,
open a new issue and include a link to the original issue in the body of your new one.

### Pull Requests

New contributions are added to this repository through Github pull requests. Make a
[fork of this repository](https://github.com/Chilipp/Climate12K-Analysis/fork) to your own Github account
and then create a new pull request with the necessary changes.

Please make sure that you

* Document new code based on the [Documentation Styleguide](#documentation-styleguide)
* End all files with a newline and follow the [PEP8](https://www.python.org/dev/peps/pep-0008/), e.g. by using [flake8](https://pypi.org/project/flake8/)

### Adding new tests

The automated testing framework uses `pytest` to run to run thousands of tests, one for every single
timeseries and meta information (e.g. valid temperatures, valid ages, etc.). The rather technical
setup of this test suite is outsourced to the [conftest.py](tests/conftest.py) script, the
configuration script for `pytest`. If you simply want to add a new test to the framework, just add a
function to the [test_data.py](tests/test_data.py) script and make sure it starts with `test_`. Then,
`pytest` will recognize it automatically and run it for every timeseries.

`pytest` uses so-called fixtures to collect the tests and provide these as input argument to the
test function. For example, if you would, for example, add a test to check that every LiPD file has a
DOI in the publications, you can define a function such as

```python
def test_has_publication(lipd_data):
    for pub in lipd_data['pub']:
        assert 'doi' in pub
```

This function will then be ran for every single LiPD file that has a temperature series in it.
`lipd_data` thereby is the python dictionary that is obtained from the
[lipd.readLipd](http://nickmckay.github.io/LiPD-utilities/python) function. This works for any of
the following fixtures that are defined in [conftest.py](tests/conftest.py):

- `lipd_file`:
  The path to a LiPD file
- `lipd_data`:
  The dictionary of a LiPD file as obtained from the [lipd.readLipd](http://nickmckay.github.io/LiPD-utilities/python)
  function. This fixture is only provided for LiPD files that contain temperature series.
- `series_data`: One individual temperature series dictionary as obtained from the
  [lipd.extractTs](http://nickmckay.github.io/LiPD-utilities/python) function
- `pd_series`: One individual `series_data` as a [pandas series](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html).
  The index is the `age` of the sample, the values are the corresponding temperatures.
- `series_data_country`: The same as `series_data` but with an additonal `geo_natEarth` country
  that corresponds to the country inferred from the [NaturalEarth shapefile](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/).

#### Extracting information to `results.xlsx`

The test suite generates an excel report that contains some important information for every time series (
e.g. `minT` in the `test_temperature_values` function. If you want to add new information here, use the
`record_property` fixture in the test function.

Following our above example, let's not only test for the doi in the  publications, but also extract the number
of publications for each LiPD file. This information should appear in the `nPublications` column of the
Excel file. We can do so by adding one single line: `record_property('nPublications', len(lipd_data['pub']))`
to our test function above and adding the `record_property` fixture to the function arguments

```python
def test_has_publication(lipd_data, record_property):
    record_property('nPublications', len(lipd_data['pub']))
    for pub in lipd_data['pub']:
        assert 'doi' in pub
```

Furthermore, to provide a bit more documentation in the Excel file, we recommend to

1. Add a docstring what the test is doing
2. Use the `record_property_name` fixture to document what the `nPublications`
  mean

The final test function than looks like

```python
def test_has_publication(
        lipd_data, record_property, record_property_name):
    """Test the number of publications and their DOI"""
    record_property_name(nPublications="Number of Publications in the LiPD file")
    record_property('nPublications', len(lipd_data['pub']))
    for pub in lipd_data['pub']:
        assert 'doi' in pub
```


### Adding new analysis notebooks
We want to make the Climate12K database more accessible so we very much welcome
contributions to play around with the data!

New notebooks should be created in the [notebooks](notebooks) directory and
should be self-explanatory, i.e. make sure you add enough comments to let the
user follow what the notebook is doing. If you need further packages to run the
analysis, you should also add them to the [environment.yml](environment.yml)
file. This makes sure that everyone can run your awesome analysis for
free on mybinder.org.

More information about jupyter notebooks can be found at https://jupyter.org.


## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line (summary) to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Documentation Styleguide

* Follow the [numpy documentation guidelines](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt).
* Use [reStructuredText](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) in the
  function documentation.
