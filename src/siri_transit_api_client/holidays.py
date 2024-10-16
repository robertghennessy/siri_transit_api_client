"""
Description: This file contains a function to get the holidays for a transit operator.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def holidays(client, operator_id: str, accept_language: str = None) -> dict:
    """
    Query the 511 api to get the holidays for a transit operator.

    :param client: SiriClient session
    :type client: siri_transit_api_client.SiriClient

    :param operator_id: filter a particular operator id/code
    :type operator_id: str

    :param accept_language: select desired language. if unsupported, will return default language.
    :type accept_language: str, optional

    :return: Results of the query
    :rtype: dict
    """

    params = {"Operator_id": operator_id}
    if accept_language:
        params["accept_language"] = accept_language

    return client._request("holidays", params)
