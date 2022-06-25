"""Tests for car_time file."""
import pytest
import siri_transit_api_client
from siri_transit_api_client import siri_client
import time
import responses


class TestSiriClient:
    def test_no_api_key(self):
        with pytest.raises(ValueError) as e_info:
            client = siri_client.SiriClient()

    def test_invalid_api_key(self):
        with pytest.raises(siri_transit_api_client.exceptions.ApiError) as e_info:
            client = siri_client.SiriClient(api_key="invalid-key")
            client.stop_monitoring("CT")

    def test_generate_auth_url(self):
        param_dict = {"agency": "CT"}
        url = "StopMonitoring"
        client = siri_client.SiriClient(api_key="fake-key")
        output_str = client._generate_auth_url(url, param_dict)
        assert output_str == "StopMonitoring?api_key=fake-key&Format=json&agency=CT"

    def test_generate_auth_url_no_optional(self):
        param_dict = {}
        url = "StopMonitoring"
        client = siri_client.SiriClient(api_key="fake-key")
        output_str = client._generate_auth_url(url, param_dict)
        assert output_str == "StopMonitoring?api_key=fake-key&Format=json"

    @responses.activate
    def test_queries_per_second(self):
        # This test assumes that the time to run a mocked query is
        # relatively small, eg a few milliseconds. We define a rate of
        # 3 queries per second, and run double that, which should take at
        # least 1 second but no more than 2.
        queries_per_second = 3
        query_range = range(queries_per_second * 2)
        for _ in query_range:
            responses.add(
                responses.GET,
                "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&Format=json&agency=CT",
                body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT","Status":"true","StopMonitoringDelivery":{}}}',
                status=200,
                content_type="application/json",
            )
        client = siri_client.SiriClient(
            api_key="fake-key", queries_per_second=queries_per_second
        )
        start = time.time()
        for _ in query_range:
            client.stop_monitoring("CT")
        end = time.time()
        assert start + 1 < end < start + 2

    @responses.activate
    def test_key_sent(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&Format=json&agency=CT",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT","Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT")

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&Format=json&agency=CT"
        )

    @responses.activate
    def test_timeout(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            status=408,
        )

        # TODO - this test function does not work. Throws http error instead of transport error

        # client = siri_client.SiriClient(api_key="fake-key")
        # client.stop_monitoring("CT")

        # assert len(responses.calls) == 1
        # assert responses.calls[0].request.url == "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT"

    @responses.activate
    def test_retry(self):

        responses.add_callback(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            content_type="application/json",
            callback=RequestCallback(),
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT")

        assert len(responses.calls) == 2
        assert responses.calls[0].request.url == responses.calls[1].request.url

    @responses.activate
    def test_retry_api_false(self):
        responses.add_callback(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            content_type="application/json",
            callback=RequestCallback(),
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT")

        assert len(responses.calls) == 2
        assert responses.calls[0].request.url == responses.calls[1].request.url

    @responses.activate
    def test_retry_intermittent(self):
        responses.add_callback(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            content_type="application/json",
            callback=RequestCallback(),
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT")

        assert len(responses.calls) == 2
        assert responses.calls[0].request.url == responses.calls[1].request.url

    @responses.activate
    def test_transport_error(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            status=404,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="invalid-key")
        with pytest.raises(Exception) as e_info:
            client.stop_monitoring("CT")

        assert e_info.typename == "TransportError"

    @responses.activate
    def test_retry_timeout(self):
        # This test assumes that the time to run a mocked query is
        # relatively small, eg a few milliseconds. We define a rate of
        # 3 queries per second, and run double that, which should take at
        # least 1 second but no more than 2.
        queries_per_second = 3
        query_range = range(queries_per_second * 3)
        for _ in query_range:
            responses.add(
                responses.GET,
                "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&Format=json&agency=CT",
                body='{"status":"Internal Server Error.","results":[]}',
                status=500,
                content_type="application/json",
            )
        client = siri_client.SiriClient(
            api_key="fake-key", retry_timeout=2, queries_per_second=3
        )
        start = time.time()

        with pytest.raises(Exception) as e_info:
            for _ in query_range:
                client.stop_monitoring("CT")

        end = time.time()
        assert start + 2 < end < start + 3
        assert e_info.typename == "Timeout"

    @responses.activate
    def test_custom_extract(self):
        def custom_extract(resp):
            return resp.json()

        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&Format=json",
            body='{"error":"errormessage"}',
            status=403,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        b = client._request("StopMonitoring", {}, extract_body=custom_extract)
        assert len(responses.calls) == 1
        assert b["error"] == "errormessage"


"""
    @responses.activate
    def test_api_error(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&Format=json&agency=CT",
            body='{"status":"Error","results":[]}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        with pytest.raises(Exception) as e_info:
            client.stop_monitoring("CT")

        assert e_info.typename == 'ApiError'
"""


class RequestCallback:
    def __init__(self):
        self.first_req = True

    def __call__(self, req):
        if self.first_req:
            self.first_req = False
            return 200, {}, '{"ServiceDelivery": { "Status": "false"}}'
        return 200, {}, '{"ServiceDelivery": { "Status": "true"}}'
