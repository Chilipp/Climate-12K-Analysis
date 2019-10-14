"""Test module for the Temperature12K data"""
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


def test_lipd_validity(lipd_file, tmp_path, accepted, record_property,
                       record_property_name):
    """Test whether the lipd file can be loaded"""

    # Extract some meta data for results.xlsx
    record_property_name(
        'validFile', 'True if the LiPD file could be loaded into Python')
    record_property('validFile', False)

    base = osp.basename(lipd_file)
    shutil.copyfile(lipd_file, str(tmp_path / base))
    with remember_cwd():
        os.chdir(str(tmp_path))
        assert accepted or lipd.readLipd('.')
    record_property('valid file', True)


def test_temperature_values(pd_series, accepted, record_property,
                            record_property_name):
    """Test whether the temperature values are within -40 and +50 degC"""
    invalid = pd_series.size - pd_series.notnull().sum()

    record_property_name(
        invalidTemperatures=("Number of temperatures in the time series that "
                             "are NaN (not a number)."),
        minT="Lowest temperature in the time series",
        maxT="Highest temperature in the time series")

    record_property('invalidTemperatures', invalid)
    record_property('minT', pd_series.min())
    record_property('maxT', pd_series.max())
    assert accepted or (pd_series.isnull() | (pd_series > -40)).all(), \
        'Too low temperatures!'
    assert accepted or (pd_series.isnull() | (pd_series < 50)).all(), \
        'Too high temperatures!'


def test_latlon(series_data, accepted, record_property, record_property_name):
    """
    Test whether the latitude is between -90 and 90 and longitude between
    -180 and 360"""
    lat = series_data['geo_meanLat']
    lon = series_data['geo_meanLon']

    record_property_name(
        latValid="True if the latitude is between -90 and 90",
        lonValid="True if the longitude is between -180 and 360",
        googleMapsUrl="The link to the location on Google Maps")

    record_property('latValid', lat >= -90 and lat <= 90)
    record_property('lonValid', lon >= -180 and lon <= 360)
    record_property(
        'googleMapsUrl',
        f'https://www.google.com/maps/search/?api=1&query={lat},{lon}')

    assert accepted or lat >= -90 and lat <= 90, 'Invalid latitudes'
    assert accepted or lon >= -180 and lon <= 360, 'Invalid longitudes'


def test_min_age(pd_series, record_property, accepted, record_property_name):
    """Test if the youngest age is larger than -70 BP"""
    ages = pd_series.index.to_series()

    record_property_name(
        minAge=("The youngest age of the timeseries (should not be smaller "
                "than -70 BP!)"))

    record_property('minAge', ages.min())

    assert accepted or ages.min() > -70, "Invalid modern age"


def test_max_age(pd_series, accepted, record_property, record_property_name):
    """Test if the oldest age is smaller than 200k BP"""
    ages = pd_series.index.to_series()

    record_property_name(
        minAge=("The oldest age of the timeseries (should not be smaller "
                "than 200k BP!)"))

    record_property('maxAge', ages.max())

    assert accepted or ages.max() < 200000, "unrealistically old age"


def test_anomaly(pd_series, accepted, record_property, record_property_name):
    """
    Test if a time series represents temperature anomalies by checking the
    temperature of the youngest samples"""
    pd_series = pd_series[~pd_series.index.duplicated()]
    youngest = pd_series.loc[[pd_series.idxmin()]].min()

    record_property_name(youngestT="Temperature of the youngest sample")

    record_property('youngestT', youngest)

    assert accepted or abs(youngest) > 1e-4, \
        "Youngest reconstruction close to 0!"


def test_elev(series_data, accepted, record_property, record_property_name):
    """Test if the elevation of marine sites is below 0"""
    elev = series_data['geo_meanElev']

    record_property_name(elevation="Elevation of the site")

    record_property('elevation', elev)

    if 'marine' in series_data['archiveType'].lower():
        assert accepted or elev <= 0


def test_duplicated_ages(pd_series, accepted, record_property,
                         record_property_name):
    """Test if the temperature series has multiple samples with the same age"""
    duplicated = pd_series.index.duplicated(False).sum()

    record_property_name(
        duplicatedAges=("The number of ages in the time series that are "
                        "duplicated. Should be 0."))

    record_property('duplicatedAges', duplicated)
    assert accepted or duplicated == 0


def test_country(series_data_country, accepted, record_property,
                 record_property_name):
    """Test if the country matches the country extracted from NaturalEarth"""
    data = series_data_country

    record_property_name(
            natEarth_Country=("The country as extracted from NaturalEarth "
                              "based on the given latitude and longitude."),
            countryOcean="The countryOcean information in the LiPD file.")

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
