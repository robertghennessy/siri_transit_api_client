"""
Description: This file contains a function to perform stop monitoring queries.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def operators(client, accept_language: str = None, operator_id: str = None):
    """
    Query the 511 api to collect list of all the public transit operators within the jurisdiction.

    :param client: SiriClient
    :type client: SiriClient

    :param accept_language: Optional. If multiple languages are supported, this can be used to request data in
        desired language, If the jurisdiction does not support the response in requested language, response could be
        in default language selected by jurisdiction.
    :type accept_language: str

    :param operator_id: Optional. The operator_id parameter supports filtering based on a particular operator id/code
    :type operator_id: str
    """

    params = {}
    if accept_language:
        params["accept_language"] = accept_language
    if operator_id:
        params["Operator_id"] = operator_id

    return client._request("Operators", params)
