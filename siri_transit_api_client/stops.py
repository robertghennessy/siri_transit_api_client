"""
Description: This file contains a function to query the stop locations.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def stops(client, operator_id: str, accept_language: str = None,  line_id: str = None, include_stop_areas: bool = False,
          direction_id: str = None, pattern_id: str = None):
    """
    Query  api to get location where passengers can board or leave from vehicles.

    :param client: SiriClient session
    :type client: SiriClient

    :param operator_id: filters based on a particular operator id/code
    :type operator_id: str

    :param accept_language: select desired language. if language unsupported, will return default language.
    :type accept_language: str, optional

    :param line_id:filter based on particular line
    :type line_id: str, optional

    :param include_stop_areas: When true, all stop areas (stop groupings) along with the referenced stops
        (ScheduledStopPoints) are returned.
    :type include_stop_areas: bool, optional

    :param direction_id: filter  based on a particular route and direction. line_id also needs to be provided. The
        direction_id should correspond to value returned by the Pattern API for the operator and route.
    :type direction_id: str, optional

    :param pattern_id: filter based on a particular pattern. The pattern_id should correspond to the id attribute of a
        ServiceJourneyPattern returned by the Pattern API.
    :type pattern_id: str, optional
    """

    params = {"Operator_id": operator_id}
    if accept_language:
        params["accept_language"] = accept_language
    if line_id:
        params["Line_id"] = line_id
    if include_stop_areas:
        params["include_stop_areas"] = "true"
    if direction_id:
        params["Direction_id"] = direction_id
    if pattern_id:
        params["Pattern_id"] = pattern_id
    return client._request("stops", params)
