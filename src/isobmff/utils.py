

def parse_iso639_2_15bit(value):
    s = chr((value >> 10 & 0x1F) + ord('a') - 1)
    s += chr((value >> 5 & 0x1F) + ord('a') - 1)
    s += chr((value & 0x1F) + ord('a') - 1)
    return s

def get_utc_from_seconds_since_1904(seconds):
    from datetime import datetime, timedelta
    return datetime(1904, 1, 1) + timedelta(days = seconds / 86400, seconds = seconds % 86400)

