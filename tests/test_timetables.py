from siri_transit_api_client import siri_client
import responses
import datetime as dt


class TestTimetables:
    @responses.activate
    def test_no_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/timetable?api_key=fake-key&Format=json&Operator_id=CT&Line_id=L5&IncludeSpecialService=False",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.timetable("CT", "L5")

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/timetable?api_key=fake-key&Format=json&Operator_id=CT&Line_id=L5&IncludeSpecialService=False"
        )

    @responses.activate
    def test_all_optional_params(self):
        responses.add(
            responses.GET,
            "https://api.511.org/Transit/timetable?api_key=fake-key&Format=json&Operator_id=CT&Line_id=L5&"
            "accept_language=en&IncludeDayTypeAssignments=True&IncludeSpecialService=True&ExceptionDate=20220605",
            body='{"ServiceDelivery":{"ResponseTimestamp":"2022-05-20T22:27:30Z","ProducerRef":"CT",'
            '"Status":"true","StopMonitoringDelivery":{}}}',
            status=200,
            content_type="application/json",
        )

        client = siri_client.SiriClient(api_key="fake-key")
        client.timetable("CT", "L5", "en", True, True, dt.date(2022, 6, 5))

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.url
            == "https://api.511.org/Transit/timetable?api_key=fake-key&Format=json&Operator_id=CT&Line_id=L5&"
            "accept_language=en&IncludeDayTypeAssignments=True&IncludeSpecialService=True&ExceptionDate=20220605"
        )
