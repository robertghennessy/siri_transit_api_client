from siri_transit_api_client import siri_client
import responses


class TestPatterns:

    @responses.activate
    def test_no_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/patterns?api_key=fake-key&Format=json&Operator_id=CT&Line_id=L5",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
                 '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.patterns('CT', 'L5')

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == \
               "https://api.511.org/Transit/patterns?api_key=fake-key&Format=json&Operator_id=CT&Line_id=L5"

    @responses.activate
    def test_all_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/patterns?api_key=fake-key&Format=json&Operator_id=CT&Line_id=L5&"
            "accept_language=en&Pattern_id=214512",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
                 '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.patterns('CT', 'L5', 'en', '214512')

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == \
               "https://api.511.org/Transit/patterns?api_key=fake-key&Format=json&Operator_id=CT&Line_id=L5&" \
               "accept_language=en&Pattern_id=214512"
