"""
Description: This file contains a function to perform vehicle monitoring queries.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def vehicle_monitoring(client, agency: str, vehicle_id: str = None) -> dict:
    """
    Collect stop monitoring information which provides current and forthcoming vehicles arrivals and departures at
    a stop.

    :param client: SiriClient session
    :type client: siri_transit_api_client.SiriClient

    :param agency: agency ID to be monitored
    :type agency: str

    :param vehicle_id:  vehicle ID to be monitored
    :type vehicle_id: str, optional

    :return: Results of the query
    :rtype: dict
    """
    params = {"agency": agency}
    if vehicle_id:
        params["vehicleID"] = vehicle_id

    return client._request("VehicleMonitoring", params)
