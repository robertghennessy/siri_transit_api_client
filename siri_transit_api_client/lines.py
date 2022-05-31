"""
Description: This file contains a function to get the routes covered by transit operator.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def lines(client, accept_language: str = None, operator_id: str = None, line_id: str = None):
    """
    Query the 511 api to get the routes covered by transit operators within the jurisdiction. Consumers can request
    list of all the routes within an operator, or they can use additional filters like line id to restrict the results
    as per their needs and use case.

    :param client: SiriClient
    :type client: SiriClient

    :param accept_language: Optional. If multiple languages are supported, this can be used to request data in
        desired language, If the jurisdiction does not support the response in requested language, response could be
        in default language selected by jurisdiction.
    :type accept_language: str

    :param operator_id: Optional. The operator_id parameter supports filtering based on a particular operator id/code
    :type operator_id: str

    :param line_id: Optional. line_id parameter supports filtering based on a particular line
    :type line_id: str
    """

    params = {}
    if accept_language:
        params["accept_language"] = accept_language
    if operator_id:
        params["Operator_id"] = operator_id
    if line_id:
        params["Line_id"] = line_id

    return client._request("lines", params)
