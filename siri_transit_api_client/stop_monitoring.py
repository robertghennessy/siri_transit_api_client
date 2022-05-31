"""
Description: This file contains a function to perform stop monitoring queries.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def stop_monitoring(client, agency: str, stop_code: str = None):
    """
    Query the 511 api to collect stop monitoring information. Siri Stop Monitoring service provides current and
    forthcoming vehicles arrivals and departures at a stop.

    :param client: SiriClient
    :type client: SiriClient

    :param agency: string that contains agency ID to be monitored
    :type agency: str

    :param stop_code: Optional string that contains stop ID to be monitored
    :type stop_code: str
    """
    params = {
        'agency': agency
    }
    if stop_code:
        params["stopCode"] = stop_code

    return client._request("StopMonitoring", params)
