# -*- coding: utf-8 -*

import struct

class MachineCmd(object):
    """
        define the structure of the data, little-endian
        h is for 2 byte integer, see the full list here https://docs.python.org/3/library/struct.html#format-characters
        add as many data types as you want to send to arduino
    """

    def __init__(self):
        self.cmd_struct = struct.Struct('<hhhhh')
        self.packet = ''
        self.d1 = 0
        self.d2 = 0
        self.d3 = 0
        self.d4 = 0
        self.d5 = 0

    def serialize(self):
        self.packet = self.cmd_struct.pack(self.d1, self.d2, self.d3, self.d4, self.d5)

    def to_hex(self):
        return self.packet.hex()

    def set_values(self, d1=0, d2=0, d3=0, d4=0, d5=0):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5

    def read(self, line=False, size=1):
        if line is True:
            return self.arduino.readline()
        else:
            return self.arduino.read(size=size)
