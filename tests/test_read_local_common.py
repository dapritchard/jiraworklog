#!/usr/bin/env python3

from jiraworklog.read_local_common import make_parse_duration
import pytest

units = {
    'w': 604800,  # number of seconds in a week
    'd':  86400,  # number of seconds in a day
    'h':   3600,  # number of seconds in an hour
    'm':     60,  # number of seconds in a minute
    's':      1   # number of seconds in a second
}
parse_duration = make_parse_duration('t')


def test_make_parse_duration_empty():
    """Empty duration string"""

    actual = parse_duration({'t': ''})
    expected = 0
    assert actual == expected

    actual = parse_duration({'t': '   '})
    expected = 0
    assert actual == expected


def test_make_parse_duration_solo():
    """Each unit by itself"""

    actual0 = parse_duration({'t': '0w'})
    actual1 = parse_duration({'t': '1w'})
    actual15 = parse_duration({'t': '15w'})
    assert actual0 == 0 * units['w']
    assert actual1 == 1 * units['w']
    assert actual15 == 15 * units['w']

    actual0 = parse_duration({'t': '0d'})
    actual1 = parse_duration({'t': '1d'})
    actual15 = parse_duration({'t': '15d'})
    assert actual0 == 0 * units['d']
    assert actual1 == 1 * units['d']
    assert actual15 == 15 * units['d']

    actual0 = parse_duration({'t': '0h'})
    actual1 = parse_duration({'t': '1h'})
    actual15 = parse_duration({'t': '15h'})
    assert actual0 == 0 * units['h']
    assert actual1 == 1 * units['h']
    assert actual15 == 15 * units['h']

    actual0 = parse_duration({'t': '0m'})
    actual1 = parse_duration({'t': '1m'})
    actual15 = parse_duration({'t': '15m'})
    assert actual0 == 0 * units['m']
    assert actual1 == 1 * units['m']
    assert actual15 == 15 * units['m']

    actual0 = parse_duration({'t': '0s'})
    actual1 = parse_duration({'t': '1s'})
    actual15 = parse_duration({'t': '15s'})
    assert actual0 == 0 * units['s']
    assert actual1 == 1 * units['s']
    assert actual15 == 15 * units['s']

    actual_ws_left = parse_duration({'t': '  1w'})
    actual_ws_right = parse_duration({'t': '1w  '})
    actual_ws_both = parse_duration({'t': '  1w  '})
    assert actual_ws_left == 1 * units['w']
    assert actual_ws_right == 1 * units['w']
    assert actual_ws_both == 1 * units['w']

    actual_ws_left = parse_duration({'t': '  1s'})
    actual_ws_right = parse_duration({'t': '1s  '})
    actual_ws_both = parse_duration({'t': '  1s  '})
    assert actual_ws_left == 1 * units['s']
    assert actual_ws_right == 1 * units['s']
    assert actual_ws_both == 1 * units['s']


def test_make_parse_duration_multipleunits():
    """Multiple units"""

    # All units
    actual_0 = parse_duration({'t': '1w 2d 3h 10m 30s'})
    actual_1 = parse_duration({'t': '  1w 2d 3h 10m 30s  '})
    actual_2 = parse_duration({'t': '1w2d3h10m30s'})
    expected = (
        1*units['w'] + 2*units['d'] + 3*units['h'] + 10*units['m'] + 30*units['s']
    )
    assert actual_0 == expected
    assert actual_1 == expected
    assert actual_2 == expected

    # Some but not all units
    actual_0 = parse_duration({'t': '2d 10m'})
    actual_1 = parse_duration({'t': '  2d 10m  '})
    actual_2 = parse_duration({'t': '2d10m'})
    expected = 2*units['d'] + 10*units['m']
    assert actual_0 == expected
    assert actual_1 == expected
    assert actual_2 == expected


def test_make_parse_duration_invalidkey():
    """Invalid key"""

    with pytest.raises(KeyError):
        parse_duration({})

    with pytest.raises(KeyError):
        parse_duration({'wrongkey': ''})


def test_make_parse_duration_invalidformat():
    """Invalid duration string"""

    # No space allowed between count and unit
    with pytest.raises(RuntimeError):
        parse_duration({'t': '9 h'})

    # Missing count
    with pytest.raises(RuntimeError):
        parse_duration({'t': '9h m'})

    # Missing count
    with pytest.raises(RuntimeError):
        parse_duration({'t': 'h 6m'})

    # Invalid unit
    with pytest.raises(RuntimeError):
        parse_duration({'t': '9Z'})

    # Invalid unit
    with pytest.raises(RuntimeError):
        parse_duration({'t': '9hm'})

    # Invalid count
    with pytest.raises(RuntimeError):
        parse_duration({'t': '0x3h m'})

    # Invalid count
    with pytest.raises(RuntimeError):
        parse_duration({'t': '2 3h m'})

    # Negative count
    with pytest.raises(RuntimeError):
        parse_duration({'t': '-9h'})
