import struct

def calc_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos 
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return struct.unpack(">H",struct.pack("<H",crc))

data = bytearray.fromhex("300313b30001")
crc = calc_crc(data)
print("%04X"%(crc))

val = hex(1059)
print(val)