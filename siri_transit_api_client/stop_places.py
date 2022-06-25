"""
Description: This file contains a function to get the stop locations for a transit operator.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def stop_places(
    client, operator_id: str, accept_language: str = None, stop_id: str = None
):
    """
    Query to get a named place or the physical stop where public transport may be accessed. C

    :param client: SiriClient session
    :type client: SiriClient

    :param operator_id: filter for operator
    :type operator_id: str

    :param accept_language: select desired language. if language unsupported, will return default language.
    :type accept_language: str, optional

    :param stop_id: filter for a stop
    :type stop_id: str, optional

    :return: Results of the query
    :rtype: dict
    """

    params = {"Operator_id": operator_id}
    if accept_language:
        params["accept_language"] = accept_language
    if stop_id:
        params["Stop_id"] = stop_id

    return client._request("stopPlaces", params)
