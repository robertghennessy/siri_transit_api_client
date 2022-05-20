"""
Description: This file contains a class to query Siri data from 511.org. This class takes inspiration from
https://github.com/googlemaps/google-maps-services-python

@author: Robert Hennessy (robertghennessy@gmail.com)
"""
import requests
import json
import datetime as dt
import collections

_DEFAULT_BASE_URL = "https://api.511.org/Transit/StopMonitoring?api_key="
_DEFAULT_TRANSIT_AGENCY = 'CT'
_RETRIABLE_STATUSES = {500, 503, 504}


class SiriClient:
    def __init__(self, api_key=None, base_url=_DEFAULT_BASE_URL, retry_timeout=60, queries_per_second=10,
                 retry_over_query_limit=True):
        """
        Query the 511 api to collect stop monitoring information.

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

        """
        if not base_url:
            raise ValueError("Must provide website link to API.")
        if not api_key:
            raise ValueError("Must provide transit api key.")
        self.base_url = base_url
        self.api_key = api_key
        self.retry_timeout = dt.timedelta(seconds=retry_timeout)
        self.queries_per_second = queries_per_second
        self.retry_over_query_limit = retry_over_query_limit
        # double ended queue. elements can be added to or removed from either the front (head) or back (tail)
        self.sent_times = collections.deque("", queries_per_second)

    def _request(self, url, params, first_request_time=None, retry_counter=0):
        """
        Performs the request and returns a json

        :param url: URL path for the request. Should begin with a slash.
        :type url: string

        :param params: HTTP GET parameters.
        :type params: dict or list of key/value tuples

        :param first_request_time: The time of the first request (None if no
            retries have occurred).
        :type first_request_time: datetime.datetime

        :param retry_counter: The number of this retry, or zero for first attempt.
        :type retry_counter: int

        """

        if not first_request_time:
            first_request_time = dt.datetime.now()

        elapsed = dt.datetime.now() - first_request_time
        if elapsed > self.retry_timeout:
            raise Timeout()

        if retry_counter > 0:
            # 0.5 * (1.5 ^ i) is an increased sleep time of 1.5x per iteration,
            # starting at 0.5s when retry_counter=0. The first retry will occur
            # at 1, so subtract that first.
            delay_seconds = 0.5 * 1.5 ** (retry_counter - 1)
            # Jitter this value by 50% and pause.
            time.sleep(delay_seconds * (random.random() + 0.5))

        response = requests.get(url)
        if response.status_code in _RETRIABLE_STATUSES:
            # Retry request.
            return self._request(url, params, first_request_time, retry_counter + 1)

        api_status = response.status_code
        api_reason = response.reason
        if api_status is not 200:
            raise ApiError(api_status, api_reason)
        url_content = response.content.decode('utf-8-sig')
        data = json.loads(url_content)
        return data

    def _get_body(self, response):
        if response.status_code != 200:
            raise googlemaps.exceptions.HTTPError(response.status_code)

        body = response.json()

        api_status = body["status"]
        if api_status == "OK" or api_status == "ZERO_RESULTS":
            return body

        if api_status == "OVER_QUERY_LIMIT":
            raise googlemaps.exceptions._OverQueryLimit(
                api_status, body.get("error_message"))

        raise googlemaps.exceptions.ApiError(api_status,
                                             body.get("error_message"))



class ApiError(Exception):
    """Represents an exception returned by the remote API."""
    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return str(self.status)
        else:
            return "%s (%s)" % (self.status, self.message)


class Timeout(Exception):
    """The request timed out."""
    pass


"""        if not transit_agency:
            raise ValueError("Must provide transit agency.")

                    url = (self.siri_511_api_website + self.transit_api_key + '&agency=' + self.transit_agency +
               '&Format=JSON')"""
