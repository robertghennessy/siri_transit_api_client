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
from siri_transit_api_client.holidays import holidays
from siri_transit_api_client.lines import lines
from siri_transit_api_client.operators import operators
from siri_transit_api_client.patterns import patterns
from siri_transit_api_client.stop_monitoring import stop_monitoring
from siri_transit_api_client.stop_places import stop_places
from siri_transit_api_client.stop_timetable import stop_timetable
from siri_transit_api_client.stops import stops
from siri_transit_api_client.timetable import timetable
from siri_transit_api_client.vehicle_monitoring import vehicle_monitoring

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


# load in the other methods
SiriClient.stop_monitoring = stop_monitoring
SiriClient.operators = operators
SiriClient.lines = lines
SiriClient.stops = stops
SiriClient.stop_places = stop_places
SiriClient.patterns = patterns
SiriClient.timetable = timetable
SiriClient.holidays = holidays
SiriClient.stop_timetable = stop_timetable
SiriClient.vehicle_monitoring = vehicle_monitoring
