import pytest
import contextlib
import os
import os.path as osp
import glob
import lipd
from collections import OrderedDict, defaultdict
import pandas as pd
import numpy as np
import re

import pytest_sugar


# avoid terminal output since we run a lot of tests
pytest_sugar.THEME['symbol_passed'] = ''


base = osp.abspath(osp.dirname(__file__))


data_dir = osp.join(base, '..', 'data')


all_reports = defaultdict(dict)


fixtures_re = re.compile(r'\[.+\]')


def _data_files(dir=data_dir):
    return glob.glob(osp.join(data_dir, '*.lpd'))


def pytest_addoption(parser):
    group = parser.getgroup('LiPD')
    group.addoption('--lipd-data', default=data_dir,
                    help="Directory of the LiPD files to test")


def pytest_configure(config):
    global data_dir
    data_dir = osp.abspath(config.option.lipd_data)


def read_lipds(data_dir):
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
        try:
            if not lipds:
                raise ValueError("Not yet defined")
        except (NameError, ValueError):
            read_lipds(metafunc.config.option.lipd_data)
        return metafunc.parametrize('lipd_data', list(lipds.values()),
                                    ids=list(lipds.keys()), indirect=True)
    if 'series_data' in metafunc.fixturenames:
        try:
            if not series:
                raise ValueError("Not yet defined")
        except (NameError, ValueError):
            read_lipds(metafunc.config.option.lipd_data)
        ids = list(map(lambda d: '{dataSetName}.{paleoData_TSid}'.format(**d),
                       series))
        return metafunc.parametrize('series_data', series, ids=ids,
                                    indirect=True)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    props = dict(rep.user_properties)
    import pickle
    with open('tmp.pkl', 'wb') as f:
        pickle.dump(rep, f)
    if rep.when == "call" and 'dataSetName' in props:
        props[fixtures_re.sub('', rep.nodeid)] = rep.outcome
        all_reports[props['dataSetName']].update(props)


def pytest_sessionfinish(session):
    """Export the results to Excel"""
    df = pd.DataFrame(all_reports).T.sort_index()
    df.index.names = ['dataSetName', 'TSid']
    general = df.loc[df.index.get_level_values(1).isnull()]
    TS_specific = df.loc[df.index.get_level_values(1).notnull()].reset_index(
        level=1).copy(True)

    general.index = general.index.droplevel(1)
    del general['dataSetName']

    cols = general.columns[general.notnull().any()]

    TS_specific.loc[general.index, cols] = general[cols]
    TS_specific.set_index('TSid', append=True, inplace=True)

    TS_specific.to_excel(osp.join(data_dir, 'results.xlsx'))


@pytest.fixture
def lipd_data(request):
    """The dictionary of a LiPD file"""
    return request.param


@pytest.fixture
def series_data(request):
    """The dictionary of a time series"""
    return request.param


@pytest.fixture
def pd_series(series_data):
    """A pandas series of the data"""
    meta_cols = ['geo_meanLon', 'geo_meanLat', 'dataSetName',
                 'paleoData_TSid', 'paleoData_variableName']
    return pd.Series(
        np.asarray(series_data['paleoData_values'], dtype=float),
        index=np.asarray(series_data['age'], dtype=float),
        name=tuple(series_data.get(name, np.nan) for name in meta_cols))


@pytest.fixture
def lipd_file(request):
    """The path to a lipd file"""
    return request.param
