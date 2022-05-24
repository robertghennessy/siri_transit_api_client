"""Tests for car_time file."""
import pytest
from siri_transit_api_client import siri_client
import configparser
import os
import time
import responses

# import the configuration file which has the api keys
path_current_directory = os.path.dirname(__file__)
path_config_file = os.path.abspath(os.path.join(path_current_directory, '..', 'config.ini'))
config = configparser.ConfigParser()
config.read(path_config_file)


class TestSiriClient:
    def test_no_api_key(self):
        with pytest.raises(Exception) as e_info:
            client = siri_client.SiriClient()

    def test_invalid_api_key(self):
        with pytest.raises(Exception) as e_info:
            client = siri_client.SiriClient(api_key="invalid-key")
            client.stop_monitoring("CT")

    def test_urlencode_params(self):
        param_dict = {'agency': 'CT', 'Format': 'JSON'}
        output_str = siri_client.urlencode_params(param_dict)
        assert output_str == 'agency=CT&Format=JSON'

    def test_generate_auth_url(self):
        param_dict = {'agency': 'CT', 'Format': 'JSON'}
        url = 'StopMonitoring'
        client = siri_client.SiriClient(api_key='fake-key')
        output_str = client._generate_auth_url(url, param_dict)
        assert output_str == 'StopMonitoring?api_key=fake-key&agency=CT&Format=JSON'

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
                "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
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
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT","Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT")

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT"

    @responses.activate
    def test_timeout(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            body=Exception('Timeout'),
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT")

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT"

    @responses.activate
    def test_retry(self):
        class request_callback:
            def __init__(self):
                self.first_req = True

            def __call__(self, req):
                if self.first_req:
                    self.first_req = False
                    return (500, {}, '{"ServiceDelivery": { "Status": "false"}}')
                return (200, {}, '{"ServiceDelivery": { "Status": "true"}}')

        responses.add_callback(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            content_type="application/json",
            callback=request_callback(),
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT")

        assert len(responses.calls) == 2
        assert responses.calls[0].request.url == responses.calls[1].request.url

    @responses.activate
    def test_retry_api_false(self):
        class request_callback:
            def __init__(self):
                self.first_req = True

            def __call__(self, req):
                if self.first_req:
                    self.first_req = False
                    return (200, {}, '{"ServiceDelivery": { "Status": "false"}}')
                return (200, {}, '{"ServiceDelivery": { "Status": "true"}}')

        responses.add_callback(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            content_type="application/json",
            callback=request_callback(),
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT")

        assert len(responses.calls) == 2
        assert responses.calls[0].request.url == responses.calls[1].request.url

    @responses.activate
    def test_retry_intermittent(self):
        class request_callback:
            def __init__(self):
                self.first_req = True

            def __call__(self, req):
                if self.first_req:
                    self.first_req = False
                    return (500, {}, '{"ServiceDelivery": { "Status": "false"}}')
                return (200, {}, '{"ServiceDelivery": { "Status": "true"}}')

        responses.add_callback(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            content_type="application/json",
            callback=request_callback(),
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

        assert e_info.typename == 'TransportError'

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
                "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
                body='{"status":"Internal Server Error.","results":[]}',
                status=500,
                content_type="application/json",
            )
        client = siri_client.SiriClient(api_key="fake-key", retry_timeout=2, queries_per_second=3)
        start = time.time()

        with pytest.raises(Exception) as e_info:
            for _ in query_range:
                client.stop_monitoring("CT")

        end = time.time()
        assert start + 2 < end < start + 3
        assert e_info.typename == 'Timeout'

    @responses.activate
    def test_custom_extract(self):
        def custom_extract(resp):
            return resp.json()

        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key",
            body='{"error":"errormessage"}',
            status=403,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        b = client._request("StopMonitoring", {}, extract_body=custom_extract)
        assert len(responses.calls) == 1
        assert b["error"] == "errormessage"

    @responses.activate
    def test_api_error(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            body='{"status":"Error","results":[]}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        with pytest.raises(Exception) as e_info:
            client.stop_monitoring("CT")

        assert e_info.typename == 'ApiError'
