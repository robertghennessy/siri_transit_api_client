from siri_transit_api_client import siri_client
import responses


class TestOperators:

    @responses.activate
    def test_no_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/lines?api_key=fake-key",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
                 '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.lines()

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == \
               "https://api.511.org/Transit/lines?api_key=fake-key"

    @responses.activate
    def test_all_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/lines?api_key=fake-key&accept_language=en&Operator_id=CT&Line_id=L5",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
                 '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.lines('en', 'CT', 'L5')

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == \
               "https://api.511.org/Transit/lines?api_key=fake-key&accept_language=en&Operator_id=CT&Line_id=L5"
