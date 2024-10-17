"""
Description: This file contains a class to query Siri data from 511.org. This class takes inspiration from
https://github.com/googlemaps/google-maps-services-python

@author: Robert Hennessy (robertghennessy@gmail.com)
"""
import collections
import datetime
import datetime as dt
import json
import random
import time
import urllib

import requests

import siri_transit_api_client


_DEFAULT_BASE_URL = "https://api.511.org/Transit/"
_DEFAULT_TRANSIT_AGENCY = "CT"
_RETRIABLE_STATUSES = {500, 503, 504}


class SiriClient:
    def __init__(
        self,
        api_key: str = None,
        base_url: str = _DEFAULT_BASE_URL,
        retry_timeout: int = 60,
        queries_per_second: int = 10,
        retry_over_query_limit: bool = True,
        requests_session: requests.Session = None,
        requests_kwargs: dict = None,
    ):
        """
        Create session to query the SIRI transit data from 511.org

        :param api_key: string that contains the api key for 511.org
        :type api_key: str

        :param base_url: weblink to 511 api
        :type base_url: str

        :param retry_timeout: Timeout across multiple retriable requests, in
            seconds.
        :type retry_timeout: int

        :param queries_per_second: Number of queries per second permitted.
            If the rate limit is reached, the client will sleep for the
            appropriate amount of time before it runs the current query.
        :type queries_per_second: int

        :param retry_over_query_limit: If True, requests that result in a
            response indicating the query rate limit was exceeded will be
            retried. Defaults to True.
        :type retry_over_query_limit: bool

        :param requests_session: Reused persistent session for flexibility.
        :type requests_session: requests.Session

        :param requests_kwargs: Extra keyword arguments for the requests' library
        :type requests_kwargs: dict

        """
        if not api_key:
            raise ValueError("Must provide transit api key.")
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests_session or requests.Session()
        self.retry_timeout = dt.timedelta(seconds=retry_timeout)
        self.queries_per_second = queries_per_second
        self.retry_over_query_limit = retry_over_query_limit
        # double ended queue. elements can be added to or removed from either the front (head) or back (tail)
        self.sent_times = collections.deque([0.0], maxlen=queries_per_second)
        self.requests_kwargs = requests_kwargs or {}

    def _request(
        self,
        url: str,
        params: dict,
        first_request_time: datetime.datetime = None,
        retry_counter: int = 0,
        base_url: str = None,
        extract_body=None,
        requests_kwargs: dict = None,
    ) -> dict:

        """
        Performs HTTP GET/POST with credentials, returning the body as
        JSON.

        :param url: URL path for the request. Should begin with a slash.
        :type url: string

        :param params: HTTP GET parameters.
        :type params: dict or list of key/value tuples

        :param first_request_time: The time of the first request (None if no
            retries have occurred).
        :type first_request_time: datetime.datetime

        :param retry_counter: The number of this retry, or zero for first attempt.
        :type retry_counter: int

        :param base_url: The base URL for the request. Defaults to the Maps API
            server. Should not have a trailing slash.
        :type base_url: string

        :param extract_body: A function that extracts the body from the request.
            If the request was not successful, the function should raise a
            googlemaps.HTTPError or googlemaps.ApiError as appropriate.
        :type extract_body: function

        :param requests_kwargs: Same extra keywords arg for requests as per
            __init__, but provided here to allow overriding internally on a
            per-request basis.
        :type requests_kwargs: dict

        :raises ApiError: when the API returns an error.
        :raises Timeout: if the request timed out.
        :raises TransportError: when something went wrong while trying to
            execute a request.
        """
        if base_url is None:
            base_url = self.base_url

        if not first_request_time:
            first_request_time = dt.datetime.now()

        elapsed = dt.datetime.now() - first_request_time
        if elapsed > self.retry_timeout:
            raise siri_transit_api_client.exceptions.Timeout()

        if retry_counter > 0:
            # implement full jitter algorithm
            cap = 1e3
            exp_base = 2
            multiple = 1
            delay_seconds = min(cap, multiple * exp_base ** retry_counter) * random.random()
            time.sleep(delay_seconds)

        authed_url = self._generate_auth_url(url, params)

        # Default to the client-level self.requests_kwargs, with method-level
        # requests_kwargs arg overriding.
        requests_kwargs = requests_kwargs or {}
        final_requests_kwargs = dict(self.requests_kwargs, **requests_kwargs)

        requests_method = self.session.get
        try:
            response = requests_method(base_url + authed_url, **final_requests_kwargs)
        except requests.exceptions.Timeout:
            raise siri_transit_api_client.exceptions.Timeout()
        except Exception as e:
            raise siri_transit_api_client.exceptions.TransportError(e)

        if response.status_code in _RETRIABLE_STATUSES:
            # Retry request.
            return self._request(
                url,
                params,
                first_request_time,
                retry_counter + 1,
                base_url,
                extract_body,
                requests_kwargs,
            )

        # Check if the time of the nth previous query (where n is
        # queries_per_second) is under a second ago - if so, sleep for
        # the difference.
        if self.sent_times and len(self.sent_times) == self.queries_per_second:
            elapsed_since_earliest = time.time() - self.sent_times[0]
            if elapsed_since_earliest < 1:
                time.sleep(1 - elapsed_since_earliest)

        try:
            if extract_body:
                result = extract_body(response)
            else:
                result = self._get_body(response)
            self.sent_times.append(time.time())
            return result
        except siri_transit_api_client.exceptions.RetriableRequest as e:
            # Retry request.
            return self._request(
                url,
                params,
                first_request_time,
                retry_counter + 1,
                base_url,
                extract_body,
                requests_kwargs,
            )

    def _get_body(self, response: requests.Response) -> dict:
        status_code = response.status_code
        if status_code == 400:
            raise siri_transit_api_client.exceptions.ApiError("error", response.text)
        elif status_code == 401:
            raise siri_transit_api_client.exceptions.ApiError(response.text)
        elif status_code == 404:
            raise siri_transit_api_client.exceptions.ApiError(response.text)
        elif status_code != 200:
            raise siri_transit_api_client.exceptions.HTTPError(response.status_code)

        decoded_data = response.content.decode("utf-8-sig")
        body = json.loads(decoded_data)
        if body and type(body) is list:
            return body
        if body and type(body) is dict:
            if "ServiceDelivery" in body:
                service_delivery = body.get("ServiceDelivery")
                # status is optional field so only fail if value false is returned
                api_status = service_delivery.get("Status", "true")
                if api_status is True or api_status == "true":
                    return body
                elif api_status is False or api_status == "false":
                    raise siri_transit_api_client.exceptions.RetriableRequest
            else:
                return body

        raise siri_transit_api_client.exceptions.ApiError("error", body)

    def _generate_auth_url(self, path: str, params: dict) -> str:
        """
        Returns the path and query string portion of the request URL, first
        adding any necessary parameters.

        :param path: The path portion of the URL.
        :type path: string

        :param params: URL parameters.
        :type params: dict

        :rtype: string
        """
        start_str = path + "?" + "api_key=" + str(self.api_key) + "&Format=json"
        if params:
            return start_str + "&" + urllib.parse.urlencode(params)
        else:
            return start_str

    def holidays(self, operator_id: str, accept_language: str = None) -> dict:
        """
        Query the 511 api to get the holidays for a transit operator.

        :param operator_id: filter a particular operator id/code
        :type operator_id: str

        :param accept_language: select desired language. if unsupported, will return default language.
        :type accept_language: str, optional

        :return: Results of the query
        :rtype: dict
        """

        params = {"Operator_id": operator_id}
        if accept_language:
            params["accept_language"] = accept_language

        return self._request("holidays", params)


    def lines(
        self, operator_id: str, accept_language: str = None, line_id: str = None
    ) -> dict:
        """
        Query the 511 api to get the routes covered by transit operators within the jurisdiction. Can list all routes or
        filter using line_id.

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

        return self._request("lines", params)

    def operators(self, accept_language: str = None, operator_id: str = None) -> dict:
        """
        Query api to collect list of all the public transit operators within the jurisdiction.

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

        return self._request("Operators", params)

    def patterns(
        self,
        operator_id: str,
        line_id: str,
        accept_language: str = None,
        pattern_id: str = None,
    ) -> dict:
        """
        Query  api to get the pattern,  an ordered list of stop points and time points for a Line.

        :param operator_id: filters based on a particular operator id/code
        :type operator_id: str

        :param line_id: filter based on particular line
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
        return self._request("patterns", params)

    def shapes(
        self,
        operator_id: str,
        trip_id: str,
        accept_language: str = None,
    ) -> dict:
        """
        Query  api to get the path that a vehicle travels along a trip.

        :param operator_id: filters based on a particular operator id/code
        :type operator_id: str

        :param trip_id: filter based on particular trip
        :type trip_id: str

        :param accept_language: select desired language. if language unsupported, will return default language.
        :type accept_language: str, optional

        :return: Results of the query
        :rtype: dict
        """

        params = {"Operator_id": operator_id, "trip_id": trip_id}
        if accept_language:
            params["accept_language"] = accept_language
        return self._request("shapes", params)

    def stop_monitoring(self, agency: str, stop_code: str = None) -> dict:
        """
        Collect stop monitoring information which provides current and forthcoming vehicles arrivals and departures at
        a stop.

        :param agency: agency ID to be monitored
        :type agency: str

        :param stop_code:  stop ID to be monitored
        :type stop_code: str, optional

        :return: Results of the query
        :rtype: dict
        """
        params = {"agency": agency}
        if stop_code:
            params["stopCode"] = stop_code

        return self._request("StopMonitoring", params)

    def stop_places(
        self, operator_id: str, accept_language: str = None, stop_id: str = None):
        """
        Query to get a named place or the physical stop where public transport may be accessed. C

        :param operator_id: filter for operator
        :type operator_id: str

        :param accept_language: select desired language. if language unsupported, will return default language.
        :type accept_language: str, optional

        :param stop_id: filter for a stop
        :type stop_id: str, optional

        :return: Results of the query
        :rtype: dict
        """

        params = {"Operator_id": operator_id}
        if accept_language:
            params["accept_language"] = accept_language
        if stop_id:
            params["Stop_id"] = stop_id

        return self._request("stopPlaces", params)

    def stop_timetable(
        self,
        operator_id: str,
        stop_code: str,
        line_id: str = None,
        start_time: str = None,
        end_time: str = None,
    ) -> dict:
        """
        Query the api stop static/scheduled timetables in the system for a particular stop

        :param operator_id: filters based on a particular operator id/code
        :type operator_id: str

        :param stop_code: The StopCode that uniquely identifies a physical stop or platform.
        :type stop_code: str

        :param line_id: filter based on particular line
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
        return self._request("stoptimetable", params)

    def stops(
        self,
        operator_id: str,
        accept_language: str = None,
        line_id: str = None,
        include_stop_areas: bool = False,
        direction_id: str = None,
        pattern_id: str = None,
    ) -> dict:
        """
        Query  api to get location where passengers can board or leave from vehicles.

        :param operator_id: filters based on a particular operator id/code
        :type operator_id: str

        :param accept_language: select desired language. if language unsupported, will return default language.
        :type accept_language: str, optional

        :param line_id: filter based on particular line
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

        :return: Results of the query
        :rtype: dict
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
        return self._request("stops", params)

    def timetable(
        self,
        operator_id: str,
        line_id: str,
        accept_language: str = None,
        include_day_type_assignments: bool = None,
        include_special_service: bool = False,
        exception_date: dt.date = None,
    ) -> dict:
        """
        Query  api to get the timetable for a given Line, Direction and DayType.

        :param operator_id: filters based on a particular operator id/code
        :type operator_id: str

        :param line_id: filter based on particular line
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
        return self._request("timetable", params)

    def vehicle_monitoring(self, agency: str, vehicle_id: str = None) -> dict:
        """
        Collect stop monitoring information which provides current and forthcoming vehicles arrivals and departures at
        a stop.

        :param agency: agency ID to be monitored
        :type agency: str

        :param vehicle_id:  vehicle ID to be monitored
        :type vehicle_id: str, optional

        :return: Results of the query
        :rtype: dict
        """
        params = {"agency": agency}
        if vehicle_id:
            params["vehicleID"] = vehicle_id

        return self._request("VehicleMonitoring", params)
