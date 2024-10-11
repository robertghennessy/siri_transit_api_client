import responses

from src.siri_transit_api_client import siri_client


class TestOperators:
    @responses.activate
    def test_no_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/Operators?api_key=fake-key&Format=json",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.operators()

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/Operators?api_key=fake-key&Format=json"
        )

    @responses.activate
    def test_all_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/Operators?api_key=fake-key&Format=json&accept_language=en&Operator_id=CT",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.operators("en", "CT")

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/Operators?api_key=fake-key&Format=json&accept_language=en&Operator_id=CT"
        )
