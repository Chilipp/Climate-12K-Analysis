import pytest
import pickle
import datetime as dt
import contextlib
import os
import os.path as osp
import glob
import lipd
from collections import OrderedDict, defaultdict
import pandas as pd
from functools import partial
import numpy as np
from textwrap import dedent
import re


# hide terminal output for passed tests because we are running a lot of them.
# We cannot use pytest-sugar.conf here because the value would be changed
# to None
try:
    import pytest_sugar
except ImportError:
    pass
else:
    pytest_sugar.THEME['symbol_passed'] = ''


base = osp.abspath(osp.dirname(__file__))


data_dir = osp.join(base, '..', 'data')


serialized_data = None


fixtures_re = re.compile(r'\[.+\]')

# Regex to extract the summary of a function docstring (take from docrep,
# https://github.com/Chilipp/docrep)
summary_patt = re.compile(r'(?s).*?(?=(\n\s*\n)|$)')


accepted_failures = []


def _data_files(dir=data_dir):
    return glob.glob(osp.join(data_dir, '*.lpd'))


def pytest_addoption(parser):
    group = parser.getgroup('LiPD')
    group.addoption(
        '--lipd-data', default=data_dir, metavar="DIRECTORY",
        help=("Directory of the LiPD files to test. Default: %(default)s. "
              "This might also be a filename of serialized lipd (see the "
              "--serialize-lipds option) in which case the data directory "
              "will be set to the directory of the given file."))
    group.addoption(
        '--excel-report', metavar='FILEPATH.xlsx', default=None,
        help=("Filename where where to store the final Excel test report. If "
              "not specified, it will be saved to DATADIR/results.xlsx, "
              "where DATADIR is determined by the --lipd-data option."))
    group.addoption(
        '--accepted', default=[], type=partial(np.loadtxt, dtype=str, ndmin=1),
        metavar="FILEPATH",
        help=("Text file with accepted failures. Each line in this text file "
              "must correspond to one nodeid in the tests (see the nodeid-* "
              "columns in results.xlsx)."))
    group.addoption(
        '--serialize-lipds', metavar="FILEPATH.pkl", default=False,
        help=("Save the extracted lipd files in a pickle file to fasten the "
              "initialization for the next time."))


def pytest_configure(config):
    global data_dir, serialized_data
    data_dir = osp.abspath(config.option.lipd_data)

    if osp.isfile(data_dir):  # serialized lipd data
        serialized_data = data_dir
        data_dir = osp.dirname(data_dir)

    accepted_failures.extend(config.option.accepted)


def read_lipds(data_dir, dump=None):
    try:
        if not series:
            raise ValueError("Not yet defined")
    except (NameError, ValueError):
        _read_lipds(data_dir)
        if dump:
            with open(dump, 'wb') as f:
                pickle.dump(lipds, f)


def _read_lipds(data_dir):
    global series, lipds
    if osp.isfile(data_dir):
        with open(data_dir, 'rb') as f:
            alllipds = pickle.load(f)
    else:
        with remember_cwd():
            os.chdir(data_dir)
            alllipds = OrderedDict(sorted(lipd.readLipd('.').items()))
    if 'dataSetName' in alllipds:
        alllipds = {alllipds['dataSetName']: alllipds}

    series = lipd.extractTs(alllipds)
    series = lipd.filterTs(series, 'paleoData_inCompilation == Temp12k')
    series = lipd.filterTs(
        series, 'paleoData_useInGlobalTemperatureAnalysis == TRUE')
    series = lipd.filterTs(series, 'paleoData_units == degC')

    lipds = {
        ds: alllipds[ds] for ds in set(s['dataSetName'] for s in series)}


@contextlib.contextmanager
def remember_cwd():
    cwd = os.getcwd()
    try:
        yield
    except Exception:
        raise
    finally:
        os.chdir(cwd)


def pytest_generate_tests(metafunc):
    options = metafunc.config.option
    if 'lipd_file' in metafunc.fixturenames:
        files = _data_files(options.lipd_data)
        return metafunc.parametrize(
            'lipd_file', files, indirect=True,
            ids=[osp.splitext(osp.basename(f))[0] for f in files])
    if 'lipd_data' in metafunc.fixturenames:
        read_lipds(options.lipd_data, options.serialize_lipds)
        return metafunc.parametrize('lipd_data', list(lipds.values()),
                                    ids=list(lipds.keys()), indirect=True)
    if 'series_data' in metafunc.fixturenames:
        read_lipds(options.lipd_data, options.serialize_lipds)
        ids = list(map(lambda d: '{dataSetName}.{paleoData_TSid}'.format(**d),
                       series))
        return metafunc.parametrize('series_data', series, ids=ids,
                                    indirect=True)

    if 'series_data_country' in metafunc.fixturenames:
        read_lipds(options.lipd_data, options.serialize_lipds)
        try:
            inject_countries(series)
        except ImportError:
            pass
        ids = list(map(lambda d: '{dataSetName}.{paleoData_TSid}'.format(**d),
                       series))
        return metafunc.parametrize('series_data_country', series, ids=ids,
                                    indirect=True)


def get_dataSetName_TSid(item):
    params = item.callspec.params
    key = None
    if 'pd_series' in params:
        key = params['pd_series'].name[-3:-1]
    elif 'series_data' in params:
        series_data = params['series_data']
        key = (series_data['dataSetName'], series_data['paleoData_TSid'])
    elif 'series_data_country' in params:
        series_data = params['series_data_country']
        key = (series_data['dataSetName'], series_data['paleoData_TSid'])
    elif 'lipd_file' in params:
        lipd_file = params['lipd_file']
        key = (osp.splitext(osp.basename(lipd_file))[0], None)
    return key


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at test calls, not setup/teardown
    if rep.when == "call":
        item.user_properties.append((item.originalname, rep.outcome))


def pytest_sessionfinish(session):
    """Export the results to Excel"""
    all_reports = defaultdict(dict)
    meta = {}
    testnames = set()
    for item in session.items:
        key = get_dataSetName_TSid(item)
        if key:
            props = dict(item.user_properties)
            props[item.originalname + '-id'] = item.nodeid
            meta.update(props.pop('meta_descriptions', {}))
            all_reports[key].update(props)
            testnames.add(item.originalname)
    if not all_reports:
        return

    # add the column names for the test functions based on the summary in the
    # function docstring
    for tn in testnames:
        item = next(item for item in session.items if item.originalname == tn)
        match = summary_patt.search(item.function.__doc__)
        meta[tn] = ' '.join(match.group().splitlines()) if match else ''
        meta[tn + '-id'] = f'Test id for the {tn} test of the given timeseries'

    df = pd.DataFrame(all_reports).T.sort_index()
    df.index.names = ['dataSetName', 'TSid']

    general = df.loc[df.index.get_level_values(1).isnull()]
    TS_specific = df.loc[df.index.get_level_values(1).notnull()]

    if not len(TS_specific):
        TS_specific = general

    elif len(general):  # merge the general info into the time series results

        TS_specific = TS_specific.reset_index(level=1).copy(True)

        general.index = general.index.droplevel(1)

        cols = general.columns[general.notnull().any()]

        general = general.loc[np.unique(TS_specific.index)]

        TS_specific.loc[general.index, cols] = general[cols]
        TS_specific.set_index('TSid', append=True, inplace=True)

    total_failures = pd.concat(
        [TS_specific.fillna('failed').groupby(col)[col].count()
         for col in testnames],
        axis=1, sort=True).fillna(0).T
    total_failures.loc['Total'] = total_failures.sum(axis=0)
    total_failures['Total'] = total_failures.sum(axis=1)

    general_help = dedent("""
        Welcome! This test report for the Climate12K database extracs some
        information to make the database more accessible.

        The Summary sheet shows some general statistics about how many
        individual tests have been ran, how many failed and how many succeeded.

        In the Test Results sheet you can find the outcomes of the individual
        tests. It contains one line per time series in the data and the columns
        represent the individual test outcomes and some extracted information
        that are essential for passing the tests (see below for a description
        of the column names).

        You should now review any failed test in the Test Results sheet.

        Whether a test failed or passed for a given time series, is reported in
        one of the following columns:

        {testcols}

        The data filters of Microsoft Excel can help you to extract the failed
        time series. Just go through the following steps:

            1. Activate the Test Results sheet
            2. Go to the Data tab of Excel and click the Filter button
            3. Look for one of the test name columns (see above)
            4. Filter for the datasets that failed this test

        You can also go the the last column (All tests passed) and filter for
        datasets that failed any of the tests.

        NOTE: Once you reviewed a failed test, you might realize that the data
        is alright and the test should not report a failure. For example,
        the oldest age in the core might indeed be older than 200'000 years.

        In this case, it is important that you note down the id of the
        corresponding test and communicate it to the person that is responsible
        to run them. You can find the id of a test for a given time series in
        the column that ends with -id (e.g., for the test_max_age test, this
        would be the test_max_age-id column).

    """.format(testcols=', '.join(testnames))).lstrip().splitlines()

    meta = pd.concat([
        pd.DataFrame(np.reshape(general_help, (-1, 1))),
        pd.DataFrame(['Description'], index=['Column']),
        pd.DataFrame([['']]),
        pd.DataFrame.from_dict(meta, 'index'),
        pd.DataFrame(
            ['', '', '',
             'This report has been automatically generated on %s' % (
                dt.datetime.now())]),
        ]).reset_index()

    # replace the numbers in the index with empty stings
    meta.iloc[:, 0] = meta.iloc[:, 0].str.replace(r'^\d+$', '').fillna('')

    ofile = session.config.option.excel_report or osp.join(data_dir,
                                                           'results.xlsx')
    with pd.ExcelWriter(ofile) as writer:
        meta.to_excel(writer, sheet_name='Help', header=False, startrow=2,
                      startcol=1, index=False)
        TS_specific.to_excel(writer, sheet_name='Test Results')
        total_failures.to_excel(writer, sheet_name='Summary')


@pytest.fixture(scope='session')
def lipd_data(request):
    """The dictionary of a LiPD file"""
    return request.param


@pytest.fixture(scope='session')
def series_data(request):
    """The dictionary of a time series"""
    return request.param


@pytest.fixture(scope='session')
def pd_series(series_data):
    """A pandas series of the data"""
    meta_cols = ['geo_meanLon', 'geo_meanLat', 'dataSetName',
                 'paleoData_TSid', 'paleoData_variableName']
    ret = pd.Series(
        np.asarray(series_data['paleoData_values'], dtype=float),
        index=np.asarray(series_data['age'], dtype=float),
        name=tuple(series_data.get(name, np.nan) for name in meta_cols))
    return ret[ret.index.notnull()]


@pytest.fixture(scope='session')
def lipd_file(request):
    """The path to a lipd file"""
    return request.param


@pytest.fixture(scope='session')
def series_data_country(request):
    return request.param


@pytest.fixture
def accepted(request):
    return request.node.nodeid in accepted_failures


@pytest.fixture
def record_property_name(record_property):
    def record_meta(key=None, desc=None, **kwargs):
        meta = {}
        if key is not None:
            meta[key] = desc
        meta.update(kwargs)
        record_property('meta_descriptions', meta)
    return record_meta


def inject_countries(series):
    from latlon_utils import get_country_gpd
    lon = np.array([d['geo_meanLon'] for d in series])
    lat = np.array([d['geo_meanLat'] for d in series])

    countries = get_country_gpd(lat, lon)

    for country, d in zip(countries, series):
        d['geo_natEarth'] = country
