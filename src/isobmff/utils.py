
# The iso-639-2 three letter language code is encoded as three 5 bit
# values in the range 1 to 26 for 'a' to 'z'.
def parse_iso639_2_15bit(value):
    s = chr((value >> 10 & 0x1F) + ord('a') - 1)
    s += chr((value >> 5 & 0x1F) + ord('a') - 1)
    s += chr((value & 0x1F) + ord('a') - 1)
    return s

# Time in various boxes are represented as seconds since 1904
def get_utc_from_seconds_since_1904(seconds):
    from datetime import datetime, timedelta
    return datetime(1904, 1, 1) + timedelta(days = seconds / 86400, seconds = seconds % 86400)

