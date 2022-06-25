"""
Description: This file contains a function to query the patterns.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def patterns(
    client,
    operator_id: str,
    line_id: str,
    accept_language: str = None,
    pattern_id: str = None,
) -> dict:
    """
    Query  api to get the pattern,  an ordered list of stop points and time points for a Line.

    :param client: SiriClient session
    :type client: SiriClient

    :param operator_id: filters based on a particular operator id/code
    :type operator_id: str

    :param line_id:filter based on particular line
    :type line_id: str

    :param accept_language: select desired language. if language unsupported, will return default language.
    :type accept_language: str, optional

    :param pattern_id: filter based on a particular pattern. The pattern_id should correspond to the id attribute of a
        ServiceJourneyPattern returned by the Pattern API.
    :type pattern_id: str, optional

    :return: Results of the query
    :rtype: dict
    """

    params = {"Operator_id": operator_id, "Line_id": line_id}
    if accept_language:
        params["accept_language"] = accept_language
    if pattern_id:
        params["Pattern_id"] = pattern_id
    return client._request("patterns", params)
