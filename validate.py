import zlib
def crc(s):
    return str(hex(zlib.crc32(bytes(s)) & 0xffffffff))



