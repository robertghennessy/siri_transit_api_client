"""
Description: This file contains a function to query the stop static/scheduled timetables in the system for a
    particular stop

@author: Robert Hennessy (robertghennessy@gmail.com)
"""


def stop_timetable(client, operator_id: str, stop_code: str, line_id: str = None, start_time: str = None,
                   end_time: str = None) -> dict:
    """
   Query the api stop static/scheduled timetables in the system for a particular stop

    :param client: SiriClient session
    :type client: SiriClient

    :param operator_id: filters based on a particular operator id/code
    :type operator_id: str

    :param stop_code: The StopCode that uniquely identifies a physical stop or platform.
    :type stop_code: str

    :param line_id:filter based on particular line
    :type line_id: str, optional

    :param start_time: The start date parameter allows for requesting departures within a departure window.
    :type start_time: str, optional

    :param end_time: The end date parameter allows for requesting departures within a departure window.
    :type end_time: str, optional

    :return: Results of the query
    :rtype: dict
    """

    params = {"OperatorRef": operator_id, "MonitoringRef": stop_code}
    if line_id:
        params["Line_id"] = line_id
    if start_time:
        params["StartTime"] = start_time
    if end_time:
        params["EndTime"] = end_time
    return client._request("stoptimetable", params)
