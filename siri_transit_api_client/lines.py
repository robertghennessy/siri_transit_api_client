"""
Description: This file contains a function to get the routes covered by transit operator.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def lines(client, operator_id: str, accept_language: str = None, line_id: str = None) -> dict:
    """
    Query the 511 api to get the routes covered by transit operators within the jurisdiction. Can list all routes or
    filter using line_id.

    :param client: SiriClient session
    :type client: SiriClient

    :param operator_id: filter a particular operator id/code
    :type operator_id: str

    :param accept_language: select desired language. if unsupported, will return default language.
    :type accept_language: str, optional

    :param line_id: filter based on a particular line
    :type line_id: str, optional

    :return: Results of the query
    :rtype: dict
    """

    params = {"Operator_id": operator_id}
    if accept_language:
        params["accept_language"] = accept_language
    if line_id:
        params["Line_id"] = line_id

    return client._request("lines", params)
