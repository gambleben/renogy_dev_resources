# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from array import array
from battery import Protection, Battery, Cell
from utils import *
from struct import *
from renogy import *
import struct

class RenogyCell(Cell):
    temp = None

class RenogyMulti(Battery):

    def __init__(self, port,baud):
        super(RenogyMulti, self).__init__(port,baud)
        self.type = self.BATTERYTYPE
        self.batteries = []
        self.capacity = 0
        self.voltage = 0
        self.current = 0

    BATTERYTYPE = "RenogyMulti"
    LENGTH_CHECK = 4
    LENGTH_POS = 2
    addresses = [b"\x30",b"\x31",b"\x32",b"\x33"]

    max_connnected_batteries = 4
    connected_batteries = 0
    start_battery_address = 48

    def test_connection(self):
        # call a function that will connect to the battery, send a command and retrieve the result.
        # The result or call should be unique to this BMS. Battery name or version, etc.
        # Return True if success, False for failure
        for test_address in self.addresses:
            test = Renogy(self.port, baud=self.baud_rate, address=test_address)
            if test.test_connection():
                self.batteries.append(test)
                self.connected_batteries = self.connected_batteries + 1

        if self.connected_batteries > 0:
            for b in self.batteries:
                self.capacity = self.capacity + b.capacity
            self.read_gen_data()
            return True
        else: return False

    def get_settings(self):
        # After successful  connection get_settings will be call to set up the battery.
        # Set the current limits, populate cell count, etc
        # Return True if success, False for failure
        self.max_battery_current = MAX_BATTERY_CURRENT
        self.max_battery_discharge_current = MAX_BATTERY_DISCHARGE_CURRENT

        self.max_battery_voltage = MAX_CELL_VOLTAGE * self.cell_count
        self.min_battery_voltage = MIN_CELL_VOLTAGE * self.cell_count
        return True

    def refresh_data(self):
        # call all functions that will refresh the battery data.
        # This will be called for every iteration (1 second)
        # Return True if success, False for failure
        
        for b in self.batteries:
            b.refresh_data()
        
        result = self.read_soc_data()
        result = result and self.read_cell_data()
        result = result and self.read_temp_data()

        return result

    def read_gen_data(self):
        self.hardware_version = self.batteries[0].hardware_version + " " + str(self.connected_batteries)
        logger.info(self.hardware_version)

        self.temp_sensors = 2 * self.connected_batteries

        if self.cell_count is None:
            self.cell_count = 0
            for b in self.batteries:
                for c in range(len(b.cells)):
                    self.cells.append(RenogyCell(False))
                    self.cell_count = self.cell_count + 1

        self.version = self.batteries[0].version
        return True

    def read_soc_data(self):
        self.current = 0
        self.capacity_remain = 0
        voltage = 0
        for b in self.batteries:
            self.current = self.current + b.current
            voltage = voltage + b.voltage
            self.capacity_remain = self.capacity_remain + b.capacity_remain

        self.voltage = voltage/self.connected_batteries
        self.soc = self.capacity_remain / self.capacity

        return True

    def read_cell_data(self):
        index = 0
        for b in self.batteries:
            for c in range(len(b.cells)):
                self.cells[index].voltage = b.cells[c].voltage
                self.cells[index].temp = b.cells[c].temp
                index = index + 1
        return True

    def read_temp_data(self):
        self.temp1 = self.batteries[0].temp1
        self.temp2 = self.batteries[0].temp2
        
        return True