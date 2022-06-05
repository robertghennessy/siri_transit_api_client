"""
Description: This file contains a function to query the timetable.

@author: Robert Hennessy (robertghennessy@gmail.com)
"""
import datetime as dt


def timetable(client, operator_id: str, line_id: str, accept_language: str = None,
              include_day_type_assignments: bool = None, include_special_service: bool = False,
              exception_date: dt.date = None) -> dict:
    """
    Query  api to get the timetable for a given Line, Direction and DayType.

    :param client: SiriClient session
    :type client: SiriClient

    :param operator_id: filters based on a particular operator id/code
    :type operator_id: str

    :param line_id:filter based on particular line
    :type line_id: str

    :param accept_language: select desired language. if language unsupported, will return default language.
    :type accept_language: str, optional

    :param include_day_type_assignments: DayTypeAssignments will be included only if this flag is set to true.
    :type include_day_type_assignments: bool, optional

    :param include_special_service: If set to true, exceptions for the selected line are returned
    :type include_special_service: bool, optional

    :param exception_date: provide timetable during holiday/exception date. If nothing returned, service not provide on
        that date
    :type exception_date: datetime.date, optional

    :return: Results of the query
    :rtype: dict
    """

    params = {"Operator_id": operator_id, "Line_id": line_id}
    if accept_language:
        params["accept_language"] = accept_language
    if include_day_type_assignments:
        params["IncludeDayTypeAssignments"] = include_day_type_assignments
    params["IncludeSpecialService"] = include_special_service
    if exception_date:
        params["ExceptionDate"] = exception_date.strftime("%Y%m%d")
    return client._request("timetable", params)
