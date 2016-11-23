from datetime import datetime, timedelta
from dateutil.tz import tzoffset
from pytz import UTC

import pytest
import mock
from freezegun import freeze_time

from traffic import LogParser


@pytest.fixture(scope='function')
def log_parser():
    return LogParser(datetime(2000, 10, 10, 20, 55, 36, tzinfo=UTC))


def test_parse_log(log_parser):
    line = """127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326"""
    expected = {
        "ip_address": "127.0.0.1",
        "user_identifier": "-",
        "requester": "frank",
        "timestamp": datetime(2000, 10, 10, 20, 55, 36, tzinfo=UTC),
        "request_method": "GET",
        "resource": "/apache_pb.gif",
        "protocol": "HTTP/1.0",
        "status_code": "200",
        "size": "2326"
    }
    expected_logs = {
        datetime(2000, 10, 10, 20, 55, 36, tzinfo=UTC): [expected]
    }

    actual = log_parser.parse_log(line)
    assert expected == actual
    assert log_parser.logs == expected_logs


def test_multiple_parse_logs_for_logs(log_parser):
    line_1 = """127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326"""
    line_2 = """127.0.0.1 - frank [10/Oct/2000:13:00:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326"""
    line_3 = """127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326"""
    expected_logs_keys = [
        datetime(2000, 10, 10, 13, 55, 36, tzinfo=tzoffset(None, -25200)),
        datetime(2000, 10, 10, 13, 0, 36, tzinfo=tzoffset(None, -25200))
    ]

    log_parser.parse_log(line_1)
    log_parser.parse_log(line_2)
    log_parser.parse_log(line_3)

    assert set(log_parser.logs.keys()) == set(expected_logs_keys)


@freeze_time("2012-01-01 03:21:34", tz_offset=-4)
def test_most_hits(log_parser):
    log_parser.logs = {
        datetime(2012, 1, 1, 3, 21, 34, tzinfo=UTC): [
            {"resource": "/potatoes"},
            {"resource": "/potatoes/molasses"},
            {"resource": "/blue/bird"}
        ],
        datetime(2012, 1, 1, 3, 21, 33, tzinfo=UTC): [
            {"resource": "/potatoes"}
        ],
        datetime(2010, 1, 1, 3, 21, 33, tzinfo=UTC): [
            {"resource": "/potatoes"}
        ]
    }
    expected = ("/potatoes", 3)

    actual = log_parser.most_hits()

    assert expected == actual
    assert log_parser.hits == {"blue": 1, "potatoes": 3}


def test_average_traffic(log_parser):
    log_parser.logs = {
        datetime(2012, 1, 1, 3, 21, 34, tzinfo=UTC): [
            {"resource": "/potatoes"},
            {"resource": "/potatoes/molasses"},
            {"resource": "/blue/bird"}
        ],
        datetime(2012, 1, 1, 3, 21, 33, tzinfo=UTC): [
            {"resource": "/potatoes"}
        ]
    }
    start = datetime(2012, 1, 1, 3, 21, 34, tzinfo=UTC)
    expected = 2

    actual = log_parser.average_traffic(start, 2)

    assert expected == actual


@freeze_time("2012-01-01 03:21:34", tz_offset=-4)
@mock.patch("traffic.LogParser.average_traffic")
def test_alert_normal_traffic(mock_average_traffic, log_parser):
    mock_average_traffic.return_value = 3
    now = datetime(2012, 1, 1, 3, 21, 34, tzinfo=UTC)

    actual = log_parser.alert(5)

    mock_average_traffic.assert_called_once_with(now, 120)
    assert log_parser.is_alert == False
    assert log_parser.alert_logs == []
    assert 3 == actual


@freeze_time("2012-01-01 03:21:34", tz_offset=-4)
@mock.patch("traffic.LogParser.average_traffic")
def test_alert_high_traffic(mock_average_traffic, log_parser):
    mock_average_traffic.return_value = 8
    now = datetime(2012, 1, 1, 3, 21, 34, tzinfo=UTC)

    actual = log_parser.alert(5)

    mock_average_traffic.assert_called_once_with(now, 120)
    assert log_parser.is_alert == True
    assert log_parser.alert_logs == [(now, True, 8)]
    assert 8 == actual


@freeze_time("2012-01-01 03:21:34", tz_offset=-4)
@mock.patch("traffic.LogParser.average_traffic")
def test_alert_recovered(mock_average_traffic, log_parser):
    mock_average_traffic.return_value = 3
    now = datetime(2012, 1, 1, 3, 21, 34, tzinfo=UTC)
    log_parser.is_alert = True
    log_parser.alert_logs = [(now - timedelta(seconds=1), True, 8)]

    actual = log_parser.alert(5)

    assert log_parser.is_alert == False
    assert log_parser.alert_logs == [
        (now - timedelta(seconds=1), True, 8),
        (now, False, 3)
    ]
    assert 3 == actual
