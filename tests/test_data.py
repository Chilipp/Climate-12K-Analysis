"""Test module for the Climate-12K data"""
import lipd
import shutil
import os
import os.path as osp
import contextlib
import numpy as np


@contextlib.contextmanager
def remember_cwd():
    cwd = os.getcwd()
    try:
        yield
    except Exception:
        raise
    finally:
        os.chdir(cwd)


def test_lipd_validity(lipd_file, tmp_path, record_property):
    """Test to load the lipd files"""
    record_property('dataSetName',
                    (osp.splitext(osp.basename(lipd_file))[0], None))
    record_property('valid file', False)
    base = osp.basename(lipd_file)
    shutil.copyfile(lipd_file, str(tmp_path / base))
    with remember_cwd():
        os.chdir(str(tmp_path))
        assert lipd.readLipd('.')
    record_property('valid file', True)


def test_chronology_points(lipd_data, record_property):
    """Test the existence of chronological points"""
    series = lipd.extractTs(lipd_data, 'all', 'chron')
    record_property('nchronpoints', 0)
    record_property('dataSetName', (lipd_data['dataSetName'], None))
    assert len(series), "No chronological information found!"
    chronpoints = next(
        (d for d in series if d['chronData_variableName'] == 'age14C'),
        None)
    assert chronpoints is not None, "No age14C series found!"
    vals = np.array([np.nan if val == 'nan' else val
                     for val in chronpoints['age14C']], float)
    assert len(vals) and not np.isnan(vals).all()
    record_property('nchronpoints', np.sum(~np.isnan(vals)))


def test_temperature_values(pd_series, record_property):
    """Test the validity of the temperature values"""
    record_property('dataSetName', pd_series.name[-3:-1])
    invalid = pd_series.size - pd_series.notnull().sum()
    record_property('invalid_temperatures', invalid)
    record_property('min', pd_series.min())
    record_property('max', pd_series.max())
    assert (pd_series > -40).all(), 'Too low temperatures!'
    assert (pd_series < 50).all(), 'Too high temperatures!'


def test_latlon(series_data, record_property):
    record_property('dataSetName', (series_data['dataSetName'],
                                    series_data['paleoData_TSid']))
    lat = series_data['geo_meanLat']
    lon = series_data['geo_meanLon']
    record_property('lat_valid', lat >= -90 and lat <= 90)
    record_property('lon_valid', lon >= -180 and lon <= 360)

    assert lat >= -90 and lat <= 90, 'Invalid latitudes'
    assert lon >= -180 and lon <= 360, 'Invalid longitudes'


def test_ages(pd_series, record_property):
    record_property('dataSetName', pd_series.name[-3:-1])
    ages = pd_series.index.to_series()
    record_property('min_age', ages.min())
    record_property('max_age', ages.max())
    assert ages.min() > -70, "Invalid modern age"


def test_elev(series_data, record_property):
    record_property('dataSetName', (series_data['dataSetName'],
                                    series_data['paleoData_TSid']))
    elev = series_data['geo_meanElev']
    record_property('Elevation', elev)
    if 'marine' in series_data['archiveType'].lower():
        assert elev < 0
