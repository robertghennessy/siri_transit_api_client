"""
Description: This file contains a function to get the routes covered by transit operator.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def stop_places(client, operator_id: str, accept_language: str = None, stop_id: str = None):
    """
    Query the 511 api to get a named place or the physical stop where public transport may be accessed. Consumers can
    request list of all the stop places by operator code or they can use additional filters such as stop id to restrict
    the results as per their needs and use case. For a given stop, the physical representation of the stop (StopPlace)
    and the representation of the stop as a point in the timetable (ScheduledStopPoint) will use the same stop
    identifier (id).

    :param client: SiriClient
    :type client: SiriClient

    :param accept_language: Optional. If multiple languages are supported, this can be used to request data in
        desired language, If the jurisdiction does not support the response in requested language, response could be
        in default language selected by jurisdiction.
    :type accept_language: str

    :param operator_id: Optional. The operator_id parameter supports filtering based on a particular operator id/code
    :type operator_id: str

    :param stop_id: Optional. stop_id parameter supports filtering based on a particular stop
    :type stop_id: str
    """

    params = {"Operator_id": operator_id}
    if accept_language:
        params["accept_language"] = accept_language
    if stop_id:
        params["Stop_id"] = stop_id

    return client._request("stopPlaces", params)
