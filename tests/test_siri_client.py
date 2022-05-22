"""Tests for car_time file."""
import pytest
from siri_transit_api_client import siri_client
import configparser
import os

# import the configuration file which has the api keys
path_current_directory = os.path.dirname(__file__)
path_config_file = os.path.abspath(os.path.join(path_current_directory, '..', 'config.ini'))
config = configparser.ConfigParser()
config.read(path_config_file)


def test_no_api_key():
    with pytest.raises(Exception) as e_info:
        client = siri_client.SiriClient()

"""
def test_wrong_api_key():
    api_key = 'a'
    with pytest.raises(Exception) as e_info:
        client = siri_client.SiriClient(api_key=api_key)


def test_wrong_website():
    api_key = config['keys']['Transit511Key']
    with pytest.raises(Exception) as e_info:
        client = siri_client.SiriClient(api_key=api_key, base_url='https://www.cnn.com')

"""
def test_urlencode_params():
    param_dict = {'agency': 'CT', 'Format': 'JSON'}
    str = siri_client.urlencode_params(param_dict)
    assert str == 'agency=CT&Format=JSON'



def test_generate_auth_url():
    param_dict = {'agency': 'CT', 'Format': 'JSON'}
    url = 'StopMonitoring'
    client = siri_client.SiriClient(api_key='fake-key')
    str = client._generate_auth_url(url, param_dict)
    assert str == 'StopMonitoring?api_key=fake-key&agency=CT&Format=JSON'

