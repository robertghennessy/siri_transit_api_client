"""
Description: This file contains a function to query the stop locations.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def shapes(
    client,
    operator_id: str,
    trip_id: str,
    accept_language: str = None,
) -> dict:
    """
    Query  api to get the path that a vehicle travels along a trip.

    :param client: SiriClient session
    :type client: siri_transit_api_client.SiriClient

    :param operator_id: filters based on a particular operator id/code
    :type operator_id: str

    :param trip_id: filter based on particular trip
    :type trip_id: str

    :param accept_language: select desired language. if language unsupported, will return default language.
    :type accept_language: str, optional

    :return: Results of the query
    :rtype: dict
    """

    params = {"Operator_id": operator_id, "trip_id": trip_id}
    if accept_language:
        params["accept_language"] = accept_language
    return client._request("shapes", params)
