import responses

from src.siri_transit_api_client import siri_client


class TestStops:
    @responses.activate
    def test_no_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/stops?api_key=fake-key&Format=json&Operator_id=CT",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stops("CT")

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/stops?api_key=fake-key&Format=json&Operator_id=CT"
        )

    @responses.activate
    def test_all_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/stops?api_key=fake-key&Format=json&Operator_id=CT&accept_language=en&"
            "Line_id=L5&include_stop_areas=true&Direction_id=n&Pattern_id=p1",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stops("CT", "en", "L5", True, "n", "p1")

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/stops?api_key=fake-key&Format=json&Operator_id=CT&accept_language=en&"
            "Line_id=L5&include_stop_areas=true&Direction_id=n&Pattern_id=p1"
        )

        # TODO - update the url to a real url #
