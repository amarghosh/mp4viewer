""" helper functions """

import sys
from datetime import datetime, timedelta


def error_print(s: str):
    """
    Print to stderr.
    Use this for all errors so that we can easily redirect json output to a file from command line.
    """
    print(s, file=sys.stderr)


def parse_iso639_2_15bit(value):
    """
    The iso-639-2 three letter language code is encoded as three 5 bit values
    in the range 1 to 26 for 'a' to 'z'.
    """
    s = chr((value >> 10 & 0x1F) + ord("a") - 1)
    s += chr((value >> 5 & 0x1F) + ord("a") - 1)
    s += chr((value & 0x1F) + ord("a") - 1)
    return s


def get_utc_from_seconds_since_1904(seconds):
    """Time in various boxes are represented as seconds since 1904"""
    return datetime(1904, 1, 1) + timedelta(
        days=seconds / 86400, seconds=seconds % 86400
    )


def stringify_duration(total_seconds):
    """seconds to xxh xxm xxs"""
    value = int(total_seconds)
    hours = value // 3600
    value %= 3600
    minutes = value // 60
    value %= 60
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes:02d}m")
    parts.append(f"{value:02d}s")
    return " ".join(parts)
