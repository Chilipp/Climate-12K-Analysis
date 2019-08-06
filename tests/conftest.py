import pytest
import contextlib
import os
import os.path as osp
import glob
import lipd
from collections import OrderedDict, defaultdict
import pandas as pd
from functools import partial
import numpy as np
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


all_reports = defaultdict(dict)


fixtures_re = re.compile(r'\[.+\]')


accepted_failures = []


def _data_files(dir=data_dir):
    return glob.glob(osp.join(data_dir, '*.lpd'))


def pytest_addoption(parser):
    group = parser.getgroup('LiPD')
    group.addoption('--lipd-data', default=data_dir, metavar="DIRECTORY",
                    help=("Directory of the LiPD files to test. "
                          "Default: %(default)s"))
    group.addoption(
        '--accepted', default=[], type=partial(np.loadtxt, dtype=str, ndmin=1),
        metavar="FILEPATH",
        help=("Text file with accepted failures. Each line in this text file "
              "must correspond to one nodeid in the tests (see the nodeid-* "
              "columns in results.xlsx)."))


def pytest_configure(config):
    global data_dir
    data_dir = osp.abspath(config.option.lipd_data)
    accepted_failures.extend(config.option.accepted)


def read_lipds(data_dir):
    try:
        if not series:
            raise ValueError("Not yet defined")
    except (NameError, ValueError):
        _read_lipds(data_dir)


def _read_lipds(data_dir):
    global series, lipds
    with remember_cwd():
        os.chdir(data_dir)
        lipds = OrderedDict(sorted(lipd.readLipd('.').items()))
        if 'dataSetName' in lipds:
            lipds = {lipds['dataSetName']: lipds}

        series = lipd.extractTs(lipds)
        series = lipd.filterTs(series, 'paleoData_inCompilation == Temp12k')
        series = lipd.filterTs(
            series, 'paleoData_useInGlobalTemperatureAnalysis == TRUE')
        series = lipd.filterTs(series, 'paleoData_units == degC')


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
    if 'lipd_file' in metafunc.fixturenames:
        files = _data_files(metafunc.config.option.lipd_data)
        return metafunc.parametrize(
            'lipd_file', files, indirect=True,
            ids=[osp.splitext(osp.basename(f))[0] for f in files])
    if 'lipd_data' in metafunc.fixturenames:
        read_lipds(metafunc.config.option.lipd_data)
        return metafunc.parametrize('lipd_data', list(lipds.values()),
                                    ids=list(lipds.keys()), indirect=True)
    if 'series_data' in metafunc.fixturenames:
        read_lipds(metafunc.config.option.lipd_data)
        ids = list(map(lambda d: '{dataSetName}.{paleoData_TSid}'.format(**d),
                       series))
        return metafunc.parametrize('series_data', series, ids=ids,
                                    indirect=True)

    if 'series_data_country' in metafunc.fixturenames:
        read_lipds(metafunc.config.option.lipd_data)
        try:
            inject_countries(series)
        except ImportError:
            pass
        ids = list(map(lambda d: '{dataSetName}.{paleoData_TSid}'.format(**d),
                       series))
        return metafunc.parametrize('series_data_country', series, ids=ids,
                                    indirect=True)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    props = dict(rep.user_properties)
    if rep.when == "call" and 'dataSetName' in props:
        funcname = fixtures_re.sub('', rep.nodeid)
        props[funcname] = rep.outcome
        props['nodeid-' + funcname] = rep.nodeid
        all_reports[props['dataSetName']].update(props)


def pytest_sessionfinish(session):
    """Export the results to Excel"""
    df = pd.DataFrame(all_reports).T.sort_index()
    df.index.names = ['dataSetName', 'TSid']

    general = df.loc[df.index.get_level_values(1).isnull()]
    TS_specific = df.loc[df.index.get_level_values(1).notnull()]

    if len(general):

        TS_specific = TS_specific.reset_index(level=1).copy(True)

        general.index = general.index.droplevel(1)
        del general['dataSetName']

        cols = general.columns[general.notnull().any()]

        general = general.loc[np.unique(TS_specific.index)]

        TS_specific.loc[general.index, cols] = general[cols]
        TS_specific.set_index('TSid', append=True, inplace=True)

    TS_specific.to_excel(osp.join(data_dir, 'results.xlsx'))


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
    return request.node._nodeid in accepted_failures


def inject_countries(series):
    from latlon_utils import get_country_gpd
    lon = np.array([d['geo_meanLon'] for d in series])
    lat = np.array([d['geo_meanLat'] for d in series])

    countries = get_country_gpd(lat, lon)

    for country, d in zip(countries, series):
        d['geo_natEarth'] = country
