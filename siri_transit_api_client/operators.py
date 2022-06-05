"""
Description: This file contains a function to list all the public transit operators in jurisdiction

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def operators(client, accept_language: str = None, operator_id: str = None) -> dict:
    """
    Query api to collect list of all the public transit operators within the jurisdiction.

    :param client: SiriClient session
    :type client: SiriClient

    :param accept_language: select desired language. if unsupported, will return default language.
    :type accept_language: str, optional

    :param operator_id: filter based on a particular operator id/code
    :type operator_id: str, optional

    :return: Results of the query
    :rtype: dict
    """

    params = {}
    if accept_language:
        params["accept_language"] = accept_language
    if operator_id:
        params["Operator_id"] = operator_id

    return client._request("Operators", params)
