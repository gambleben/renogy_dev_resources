from serial.serialutil import STOPBITS_TWO
import minimalmodbus

class RenogySmartBattery(minimalmodbus.Instrument):
    def __init__(self, portname="COM3", slaveaddress=48, baudrate=9600, timeout=0.5):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        self.serial.baudrate = baudrate
        self.serial.timeout = timeout
        self.debug = True

    def amps(self):
        r = self.read_register(5042)
        return r / 100.0 if r < 61440 else (r - 65535) / 100.0

    def volts(self):
        return self.read_register(5043) / 10.0

    def capacity(self):
        r = self.read_registers(5044, 2)
        return ( r[0] << 15 | (r[1] >> 1) ) * 0.002

    def max_capacity(self):
        r = self.read_registers(5046,2)
        a = r[0] << 15
        b = r[1] >> 1
        return ( r[0] << 15 | (r[1] >> 1) ) * 0.002

    def percentage(self):
        return self.capacity() / self.max_capacity() * 100

    def state(self):
        a = self.amps()
        if a < 0: return "DISCHARGING"
        elif a > 0: return "CHARGING"
        return "IDLE"

x = RenogySmartBattery()
print("test")
y = x.max_capacity()
print(y)