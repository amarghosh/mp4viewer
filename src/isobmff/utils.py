

def parse_iso639_2_15bit(value):
    s = chr((value >> 10 & 0x1F) + ord('a') - 1)
    s += chr((value >> 5 & 0x1F) + ord('a') - 1)
    s += chr((value & 0x1F) + ord('a') - 1)
    return s

