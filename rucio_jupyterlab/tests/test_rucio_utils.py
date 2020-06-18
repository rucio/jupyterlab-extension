from rucio_jupyterlab.rucio.utils import parse_timestamp


def test_parse_timestamp_returns_correct_timezone_utc():
    time_str = 'Mon, 13 May 2013 10:23:03 UTC'
    expected_output = 1368440583
    assert parse_timestamp(time_str) == expected_output, "Invalid timestamp conversion"
