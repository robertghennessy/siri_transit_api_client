import pytest
from siri_transit_api_client import siri_client
import responses
import json


class TestVehicleMonitoring:
    @responses.activate
    def test_missing_agency(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/VehicleMonitoring?api_key=fake-key&agency=CT",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        with pytest.raises(Exception) as e_info:
            client.vehicle_monitoring()

        assert e_info.typename == "TypeError"

    @responses.activate
    def test_vehicle_code_sent(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/VehicleMonitoring?api_key=fake-key&Format=json&agency=CT&vehicleID=231",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.vehicle_monitoring("CT", "231")

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/VehicleMonitoring?api_key=fake-key&Format=json&agency=CT&vehicleID=231"
        )
