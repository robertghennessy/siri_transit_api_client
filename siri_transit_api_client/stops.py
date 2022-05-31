"""
Description: This file contains a function to query the stop locations.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def stops(client, operator_id: str, accept_language: str = None,  line_id: str = None, include_stop_areas: bool = False,
          direction_id: str = None, pattern_id: str = None):
    """
    Query the 511 api to get location where passengers can board or alight from vehicles. Consumers can request list of
    all the stops serviced by an agency/operator within the jurisdiction. Stop groupings or StopAreas are also returned
    when specifically requested using the include_stop_areas parameter.

    :param client: SiriClient
    :type client: SiriClient

    :param operator_id: mandatory. The operator_id parameter supports filtering based on a particular operator id/code
    :type operator_id: str

    :param accept_language: Optional. If multiple languages are supported, this can be used to request data in
        desired language, If the jurisdiction does not support the response in requested language, response could be
        in default language selected by jurisdiction.
    :type accept_language: str

    :param line_id: Optional. line_id parameter supports filtering based on a particular line
    :type line_id: str

    :param include_stop_areas: Optional. When this parameter is set to true, all stop areas (stop groupings) along with
        the referenced stops (ScheduledStopPoints) are returned.
    :type include_stop_areas: str

    :param direction_id: Optional. The direction_id parameter supports filtering based on a particular route and
        direction. This parameter has to be provided along with the line_id parameter. The direction_id should
        correspond to the id attribute of a Direction returned by the Pattern API for the operator and route.
    :type direction_id: str

    :param pattern_id: Optional. The pattern_id parameter supports filtering based on a particular pattern. The
        pattern_id should correspond to the id attribute of a ServiceJourneyPattern returned by the Pattern API.
    :type pattern_id: str
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
