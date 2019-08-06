"""Test module for the Climate-12K data"""
import lipd
import shutil
import os
import os.path as osp
import contextlib
import numpy as np
import pytest


@contextlib.contextmanager
def remember_cwd():
    cwd = os.getcwd()
    try:
        yield
    except Exception:
        raise
    finally:
        os.chdir(cwd)


def test_lipd_validity(lipd_file, tmp_path, record_property, accepted):
    """Test to load the lipd files"""
    record_property('dataSetName',
                    (osp.splitext(osp.basename(lipd_file))[0], None))
    record_property('valid file', False)
    base = osp.basename(lipd_file)
    shutil.copyfile(lipd_file, str(tmp_path / base))
    with remember_cwd():
        os.chdir(str(tmp_path))
        assert accepted or lipd.readLipd('.')
    record_property('valid file', True)


def test_chronology_points(lipd_data, record_property, accepted):
    """Test the existence of chronological points"""
    series = lipd.extractTs(lipd_data, 'all', 'chron')
    record_property('nchronpoints', 0)
    record_property('dataSetName', (lipd_data['dataSetName'], None))
    assert len(series), "No chronological information found!"
    chronpoints = next(
        (d for d in series if d['chronData_variableName'] == 'age14C'),
        None)
    assert accepted or chronpoints is not None, "No age14C series found!"
    vals = np.array([np.nan if val == 'nan' else val
                     for val in chronpoints['age14C']], float)
    assert accepted or (len(vals) and not np.isnan(vals).all())
    record_property('nchronpoints', np.sum(~np.isnan(vals)))


def test_temperature_values(pd_series, record_property, accepted):
    """Test the validity of the temperature values"""
    record_property('dataSetName', pd_series.name[-3:-1])
    invalid = pd_series.size - pd_series.notnull().sum()
    record_property('invalid_temperatures', invalid)
    record_property('min', pd_series.min())
    record_property('max', pd_series.max())
    assert accepted or (pd_series > -40).all(), 'Too low temperatures!'
    assert accepted or (pd_series < 50).all(), 'Too high temperatures!'


def test_latlon(series_data, record_property, accepted):
    record_property('dataSetName', (series_data['dataSetName'],
                                    series_data['paleoData_TSid']))
    lat = series_data['geo_meanLat']
    lon = series_data['geo_meanLon']
    record_property('lat_valid', lat >= -90 and lat <= 90)
    record_property('lon_valid', lon >= -180 and lon <= 360)
    record_property(
        'googleMapsUrl',
        f'https://www.google.com/maps/search/?api=1&query={lat},{lon}')

    assert accepted or lat >= -90 and lat <= 90, 'Invalid latitudes'
    assert accepted or lon >= -180 and lon <= 360, 'Invalid longitudes'


def test_min_age(pd_series, record_property, accepted):
    record_property('dataSetName', pd_series.name[-3:-1])
    ages = pd_series.index.to_series()
    record_property('min_age', ages.min())
    assert accepted or ages.min() > -70, "Invalid modern age"


def test_max_age(pd_series, record_property, accepted):
    record_property('dataSetName', pd_series.name[-3:-1])
    ages = pd_series.index.to_series()
    record_property('max_age', ages.max())
    assert accepted or ages.max() < 200000, "unrealistically old age"


def test_anomaly(pd_series, record_property, accepted):
    """Test if a time series represents temperature anomalies"""
    record_property('dataSetName', pd_series.name[-3:-1])
    pd_series = pd_series[~pd_series.index.duplicated()]
    youngest = pd_series.loc[[pd_series.idxmin()]].abs().min()
    record_property('youngest_T_absolute', youngest)
    assert accepted or youngest > 1e-4, "Youngest reconstruction close to 0!"


def test_elev(series_data, record_property, accepted):
    record_property('dataSetName', (series_data['dataSetName'],
                                    series_data['paleoData_TSid']))
    elev = series_data['geo_meanElev']
    record_property('Elevation', elev)
    if 'marine' in series_data['archiveType'].lower():
        assert accepted or elev < 0


def test_duplicated_ages(pd_series, record_property, accepted):
    record_property('dataSetName', pd_series.name[-3:-1])
    duplicated = pd_series.index.duplicated(False).sum()
    record_property('duplicatedAges', duplicated)
    assert accepted or duplicated == 0


def test_country(series_data_country, record_property, accepted):
    data = series_data_country
    record_property('dataSetName', (data['dataSetName'],
                                    data['paleoData_TSid']))

    record_property('natEarth_Country', data.get('geo_natEarth', ''))
    record_property('countryOcean', data.get('geo_countryOcean', ''))

    try:
        if not data.get('geo_natEarth') or np.isnan(data['geo_natEarth']):
            pytest.skip("No natural earth data available")
            return
    except TypeError:
        pass
    assert accepted or data['geo_natEarth'].lower() in data.get(
        'geo_countryOcean', '').lower()
