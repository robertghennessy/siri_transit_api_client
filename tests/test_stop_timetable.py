from siri_transit_api_client import siri_client
import responses


class TestHolidays:
    @responses.activate
    def test_no_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/stoptimetable?api_key=fake-key&Format=json&Operator_id=CT&MonitoringRef=70021",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_timetable("CT", "70021")

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/stoptimetable?api_key=fake-key&Format=json&Operator_id=CT&MonitoringRef=70021"
        )

    @responses.activate
    def test_all_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/stoptimetable?api_key=fake-key&Format=json&Operator_id=CT&MonitoringRef=70021&Line_id=L5&StartTime=2022&EndTime=2023",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.stop_timetable("CT", "70021", "L5", "2022", "2023")

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/stoptimetable?api_key=fake-key&Format=json&Operator_id=CT&MonitoringRef=70021&Line_id=L5&StartTime=2022&EndTime=2023"
        )
