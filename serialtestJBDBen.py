# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from time import sleep
import serial
import sys
from struct import *
import binascii


def read_serial_data(command, port, baud, length_pos, length_check, length_fixed):
    try:
        with serial.Serial(port, baudrate=baud, timeout=1) as ser:
            ser.parity = serial.PARITY_NONE
            ser.stopbits = 2
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
            print(binascii.hexlify(res.hex()))
            length = length_fixed if length_fixed is not None else unpack_from('>H', res,length_pos)[0]
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



def read_gen_data():
    commandGenData = b"\x01\x03\x00\x0A\x00\x01\xA4\x08"
    #commandGenData = b"\x01\x00\x03\x0C\x00\x08\x84\x0F"

    res = read_serial_data(commandGenData, 'COM3', 9600, 3, 6, False)

    print(sys.getsizeof(res))
    print(res.hex())

    start, flag, command_ret, length = unpack_from('BBBB', res)
    checksum, end = unpack_from('HB', res, length + 4)

    print("start=" + str(start))
    print("length=" + str(length))
    print("flag=" + str(flag))
    print("command=" + str(command_ret))
    print("checksum=" + str(checksum))
    print("end=" + str(end))
    

for x in range(1):
    read_gen_data()
    sleep(5)
    print()
