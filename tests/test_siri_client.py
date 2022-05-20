"""Tests for car_time file."""
import pytest
from transit_vs_car_v2 import siri_client
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


def test_wrong_api_key():
    transit_api_key = 'a'
    siri_rt_api_website = config['siri_511']['siri_511_api']
    transit_agency = config['siri_511']['agency']
    with pytest.raises(Exception) as e_info:
        client = siri_client.SiriClient(transit_api_key, siri_rt_api_website, transit_agency)
        data = client._request()


def test_wrong_website():
    transit_api_key = config['keys']['Transit511Key']
    siri_rt_api_website = 'a'
    transit_agency = config['siri_511']['agency']
    with pytest.raises(Exception) as e_info:
        client = siri_client.SiriClient(transit_api_key, siri_rt_api_website, transit_agency)


def test_wrong_transit_agency():
    transit_api_key = config['keys']['Transit511Key']
    siri_rt_api_website = config['siri_511']['siri_511_api']
    transit_agency = 'a'
    with pytest.raises(Exception) as e_info:
        client = siri_client.SiriClient(transit_api_key, siri_rt_api_website, transit_agency)



def test_SiriClient():
    transit_api_key = config['keys']['Transit511Key']
    siri_rt_api_website = config['siri_511']['siri_511_api']
    transit_agency = config['siri_511']['agency']
    client = siri_client.SiriClient(transit_api_key, siri_rt_api_website, transit_agency)
