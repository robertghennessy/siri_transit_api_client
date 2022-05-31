import pytest
from siri_transit_api_client import siri_client
import responses
import json


class TestStopMonitoring:

    @responses.activate
    def test_missing_agency(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
                 '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        with pytest.raises(Exception) as e_info:
            client.stop_monitoring()

        assert e_info.typename == 'TypeError'

    @responses.activate
    def test_stop_code_sent(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT&stopCode=1234",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
                 '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_monitoring("CT", "1234")

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == \
               "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT&stopCode=1234"

    @responses.activate
    def test_outputted_json(self):
        input_dict = {"ServiceDelivery": {"ResponseTimestamp": "2022-05-20T22:27:30Z", "ProducerRef": "CT",
                                          "Status": "true", "StopMonitoringDelivery": {}}}
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/StopMonitoring?api_key=fake-key&agency=CT",
            json=input_dict,
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        output_dict = client.stop_monitoring("CT")
        assert type(output_dict) == dict
        assert input_dict == output_dict
