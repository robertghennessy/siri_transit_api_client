"""
Description: This file contains a function to perform stop monitoring queries.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def stop_monitoring(client, agency: str, stop_code: str = None) -> dict:
    """
    Collect stop monitoring information which provides current and forthcoming vehicles arrivals and departures at
    a stop.

    :param client: SiriClient session
    :type client: SiriClient

    :param agency: agency ID to be monitored
    :type agency: str

    :param stop_code:  stop ID to be monitored
    :type stop_code: str, optional

    :return: Results of the query
    :rtype: dict
    """
    params = {
        'agency': agency
    }
    if stop_code:
        params["stopCode"] = stop_code

    return client._request("StopMonitoring", params)
