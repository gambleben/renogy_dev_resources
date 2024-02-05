# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from time import sleep
import serial
import sys
from struct import *
import struct
import binascii

# command bytes [Address field][Function code (03 = Read register)][Register Address (2 bytes)][Data Length (2 bytes)][CRC (2 bytes little endian)]
# Battery addresses start at 48 decimal, 30 hex
command_address = b"\x30"
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
#command_soc = b"\x13\xB4\x00\x02"                #Registers 5044-5045 (long)
command_soc = b"\x13\xB2\x00\x04"
# Battery info
command_manufacturer = b"\x14\x0C\x00\x08"       #Registers 5132-5139 (8 byte string)
command_model = b"\x14\x02\x00\x08"              #Registers 5122-5129 (8 byte string)
command_serial_number = b"\x13\xF6\x00\x08"      #Registers 5110-5117 (8 byte string)
command_firmware_version = b"\x14\x0A\x00\x02"   #Registers 5130-5131 (2 byte string)
# BMS warning and protection config
command_max_charge_current = b"\x13\xbb\x00\x01"    #Register  5051 (signed int)
command_max_discharge_current = b"\x13\xbc\x00\x01" #Register  5052 (signed int)



def read_serial_data(command, port, baud, length_pos, length_check, length_fixed):
    try:
        with serial.Serial(port, baudrate=baud, timeout=0.1) as ser:
            ser.flushOutput()
            ser.flushInput()
            print(ser.name)
            ser.write(command)

            count = 0
            toread = ser.inWaiting()

            while toread < (length_pos+1):
                sleep(0.005)
                toread = ser.inWaiting()
                count += 1
                if count > 50:
                    print(">>> ERROR: No reply - returning")
                    return False
                    
            print('serial data toread ' + str(toread))
            res = ser.read(toread)
            #print(res)
            #print(res.hex())
            #print(binascii.hexlify(res.hex()))
            #length = length_fixed if length_fixed is not None else unpack_from('>H', res,length_pos)[0]
            length = unpack_from('>B', res,length_pos)[0]
            
            print('serial data length ' + str(length))

            count = 0
            data = bytearray(res)
            while len(data) < length + length_check:
                res = ser.read(length + length_check)
                data.extend(res)
                print('serial data length - ' + str(len(data)) + ' of ' + str(length + length_check))
                sleep(0.005)
                count += 1
                if count > 150:
                    print(">>> ERROR: No reply - returning")
                    return False

            return data

    except serial.SerialException as e:
        print(e)
        return False

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
    return struct.pack('<H',crc)

def generate_command(command):
    buffer = bytearray(command_address)
    buffer += command_read
    buffer += command
    buffer += calc_crc(buffer)

    return buffer

def read_gen_data(command):
# MinimalModbus debug mode. Will write to instrument (expecting 7 bytes back): 30 03 13 B3 00 01 75 48 (8 bytes)
# MinimalModbus debug mode. Clearing serial buffers for port COM3
# MinimalModbus debug mode. Sleeping 4.01 ms before sending. Minimum silent period: 4.01 ms, time since read: 0.00 ms.
# MinimalModbus debug mode. Response from instrument: 30 03 02 00 85 04 23 (7 bytes), roundtrip time: 0.0 ms. Timeout for reading: 100.0 ms.

# Battery Voltage:  133    
    commandGenData = generate_command(command)
    #commandGenData = b"\x30\x03\x13\xb3\x00\x01\x75\x48"
    #commandGenData = b"\x7E\x32\x30\x30\x32\x34\x36\x34\x32\x45\x30\x30\x32\x30\x32\x46\x44\x33\x33\x0D"
    #commandGenData = b"\x30\x03\x13\xf0\x00\x04\x44\x9f"
    #commandGenData = b"\x30\x03\x13\xBC\x00\x01\x45\x4B"
    commandGenData = b"\xff\x03\x00\x00\x00\x01\x91\xd4"
    
    res = read_serial_data(commandGenData, 'COM3', 9600, 2, 5, False)

    print(sys.getsizeof(res))
    print(binascii.hexlify(res))

    start, flag, length = unpack_from('BBB', res)
    #checksum = unpack_from('>H', res, length + 3)
    
    print("start=" + str(start))
    print("length=" + str(length))
    print("flag=" + str(flag))
    #print("command=" + str(command_ret))
    #print("checksum=" + str(checksum[0]))
    #print("end=" + str(end))
    data = res[3:length+3]
    print(data)
    return data

for x in range(1):
    #voltage = read_gen_data(command_total_voltage)
    #voltage = unpack('>H',voltage)[0]/10
    #print(voltage)
    #soc = read_gen_data(command_soc)
    #soc = unpack('>L',soc)[0]/1000
    #print(soc)
    #soc_data = read_gen_data(command_soc)
    #current, voltage, soc = unpack_from('>hhL', soc_data)
    #current = current / 100
    #voltage = voltage / 10
    #soc = soc / 1000
    #print(current)
    #print(voltage)
    #print(soc)

    #status_data = read_gen_data(command_serial_number)
    #serial_num = str(unpack_from('16s',status_data)[0],'ascii')
    #serial_num = unpack_from('16s',status_data)[0]
    #serial_num = status_data.decode('UTF-8')
    #print(serial_num)
    #sleep(5)
    #print()
    #alarm_data = read_gen_data(command_address)
    # b1, b2, b3, b4 = unpack_from('>hhhh',alarm_data)
    # binP = ("{0:#0{1}b}".format(b1,18)).ljust(21)
    # print( binP)
    # binP = ("{0:#0{1}b}".format(b2,18)).ljust(21)
    # print( binP)
    # binP = ("{0:#0{1}b}".format(b3,18)).ljust(21)
    # print( binP)
    # binP = ("{0:#0{1}b}".format(b4,18)).ljust(21)
    # print( binP)
    value = read_gen_data(command_max_discharge_current)
    value = struct.unpack('>h',value)[0]
    print(value)