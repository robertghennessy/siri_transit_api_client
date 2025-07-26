"""Top-level package for SIRI Transit API Client."""

__author__ = """Robert G Hennessy"""
__email__ = 'robertghennessy@gmail.com'
__version__ = '0.2.1'

from siri_transit_api_client.siri_client import SiriClient
from siri_transit_api_client import exceptions

__all__ = ["SiriClient", "exceptions"]

