import struct
import binascii

# command bytes [Address field][Function code (03 = Read register)][Register Address (2 bytes)][Data Length (2 bytes)][CRC (2 bytes little endian)]
command_address = b"\x30"                       #Battery addresses start at 48 decimal, 30 hex
command_address_test = "0"
command_read = b"\x03"
# Core data = voltage, temp, current, soc
command_cell_count = b"\x13\x88\x00\x01"         #Register  5000
command_cell_voltages = b"\x13\x89\x00\x04"      #Registers 5001-5004
command_cell_temps = b"\x13\x9A\x00\x04"         #Registers 5018-5021
command_total_voltage = b"\x13\xB3\x00\x01"      #Register  5043
command_bms_temp1 = b"\x13\xAD\x00\x01"          #Register  5037
command_bms_temp2 = b"\x13\xB0\x00\x01"          #Register  5040
command_current = b"\x13\xB2\x00\x01"            #Register  5042 (signed int)
command_capacity = b"\x13\xB6\x00\x02"           #Registers 5046-5047 (long)
command_soc = b"\x13\xB4\x00\x02"                #Registers 5044-5045 (long)
# Battery info
command_manufacturer = b"\x14\x0C\x00\x08"       #Registers 5132-5139 (8 byte string)
command_model = b"\x14\x02\x00\x08"              #Registers 5122-5129 (8 byte string)
command_serial_number = b"\x13\xF6\x00\x08"      #Registers 5110-5117 (8 byte string)
command_firmware_version = b"\x14\x0A\x00\x02"   #Registers 5130-5131 (2 byte string)
# BMS warning and protection config

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
    #myval = struct.unpack(">H",struct.pack("<H",crc))
    return struct.pack('<H',crc)
    #return crc

#buffer = struct.pack('ss',command_address, command_read)
buffer = bytearray(command_address)
print(binascii.hexlify(buffer))
buffer2 = bytearray(command_address_test)
buffer2 += command_read
buffer2 += command_serial_number
buffer += command_read
buffer += command_serial_number
#buffer = b"\x30\x03\x13\xb3\x00\x01"
crcbytes = calc_crc(buffer)
#crcbytes = hex(crcbytes)
#crctest = crcbytes.to_bytes(2,'little')
#buffer += calc_crc(buffer).to_bytes(2,'little')
buffer += calc_crc(buffer)
buffer2 += calc_crc(buffer2)
print(binascii.hexlify(buffer))
print(binascii.hexlify(buffer2))
buffer3 = chr(int("0",16))
print(binascii.hexlify(buffer3))
test = buffer
