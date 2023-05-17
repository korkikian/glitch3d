# Copyright 2021 Karim Sudki
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import configparser

import click
import serial
import serial.tools.list_ports

class printer():
    def __init__(self, port=None, baudrate=115200, timeout=None):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.x_s = 0.1
        self.y_s = 0.1
        self.z_s = 0.1

        self.limits = {
            "min_x" : 0.0,
            "max_x" : 0.0,
            "min_y" : 0.0,
            "max_y" : 0.0,
            "min_z" : 0.0,
            "max_z" : 0.0,
            "min_s" : 0.1,
            "max_s" : 100.0,
        }

        if port is None:
            for port in serial.tools.list_ports.comports():
                if port.vid == 0x1A86 and port.pid== 0x7523:
                    self.port = port.device
        else:
            self.port = port

        try:
            self._serialport = serial.Serial(self.port, baudrate=115200, timeout=None)
        except serial.SerialException as e:
            raise type(e)(f"Cannot send : {e.strerror}")

    def load_settings(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        if "LIMITS" in config.sections():
            for k, v in config.items("LIMITS"):
                self.limits[k] = float(v)
                
        #Steps definition
        # [STEPS]
        # step_x = 0.01     //if x step shall be changed from the hardcoded 0.1
        # step_y = 0.01     //if y step shall be changed from the hardcoded 0.1
        # step_z = 0.01     //if z step shall be changed from the hardcoded 0.1
        # step_xyz = 0.01   //if the three steps shall be changed to the same value
        if "STEPS" in config.sections():
            for k, v in config.items("STEPS"):
                try:
                    f_val = float(v)
                    if k == 'step_x'  and f_val >= self.limits['min_s'] and f_val <= self.limits['max_s']:
                        print(f'Changing x step from {self.x_s:.2f} to {f_val:.2f}')
                        self.x_s = f_val
                    elif k == 'step_y' and f_val >= self.limits['min_s'] and f_val <= self.limits['max_s']:
                        print(f'Changing y step from {self.y_s:.2f} to {f_val:.2f}')
                        self.y_s = f_val
                    elif k == 'step_z' and f_val >= self.limits['min_s'] and f_val <= self.limits['max_s']:
                        print(f'Changing z step from {self.z_s:.2f} to {f_val:.2f}')
                        self.z_s = f_val
                    elif k == 'step_xyz' and f_val >= self.limits['min_s'] and f_val <= self.limits['max_s']:
                        print(f'Changing xyz steps from {self.x_s:.2f} {self.y_s:.2f} {self.z_s:.2f} to {f_val:.2f}')
                        self.x_s = f_val
                        self.y_s = f_val
                        self.z_s = f_val
                except:
                    print('ERROR during config conversion: ', k, v)
                else:
                    None
                finally:
                    None
        
    def write(self, data=b""):
        if not self.connected:
            raise serial.SerialException("Not connected.")
        try:
            self._serialport.write(data+b"\r")
            self._serialport.flush()
        except serial.SerialException as e:
            raise type(e)(f"Cannot send : {e.strerror}")

    def read_until(self, c=None, size=None):
        if not self.connected:
            raise serial.SerialException("Not connected.")
        try:
            data = self._serialport.read_until(expected=c, size=None)
            self._lastread = data
            return data
        except serial.SerialException as e:
            raise type(e)(f"Cannot read : {e.strerror}")

    def read(self, length=1):
        if not self.connected:
            raise serial.SerialException("Not connected.")
        try:
            data = self._serialport.read(length)
            self._lastread = data
            return data
        except serial.SerialException as e:
            raise type(e)(f"Cannot read : {e.strerror}")

    def flush_input(self):
        self._serialport.reset_input_buffer()

    def close(self):
        self._serialport.close()

    def get_timeout(self):
        return self._serialport.timeout

    def set_timeout(self, value):
        self._serialport.timeout = value

    def connected(self):
        return self._serialport.is_open

    def set_unit(self,value):
        if value == "mm":
            self.write(b"G21")
            self.read_until(c=b"ok")
            print("Switching to Metric units (millimeters)")
        elif value == "in":
            self.write(b"G20")
            self.read_until(c=b"ok")
            print("Switching to US/Imperial units (inches)")

    def go_home_xy(self):
        self.check_limits(self.x, self.y, self.z+20, self.s)
        self.set_pos(self.x, self.y, self.z+20)
        self.write(b"G28 X Y")
        self.read_until(c=b"ok")
        self.get_pos()

    def go_home_xyz(self):
        self.check_limits(self.x, self.y, self.z+20, self.s)
        self.set_pos(self.x, self.y, self.z+20)
        self.write(b"G28 X Y Z")
        self.read_until(c=b"ok")
        self.get_pos()

    def set_pos(self, x, y, z):
        #self.write(f"G0 X {x:.1f} Y {y:.1f} Z {z:.1f} F6000".encode())
        #Two-digits precision for A350
        self.write(f"G0 X {x:.2f} Y {y:.2f} Z {z:.2f} F6000".encode())
        self.read_until(c=b"ok")
        self.x = x
        self.y = y
        self.z = z
        self.get_pos()

    def get_pos(self):
        self.write(b"M114")
        #regex = re.compile(b'.*X:[-]*(?P<x>\d+.\d+)\sY:[-]*(?P<y>\d+.\d+)\sZ:[-]*(?P<z>\d+.\d+)\sE:')
        #Taking the negative coordinate values
        regex = re.compile(b'.*X:(?P<x>[-]*\d+.\d+)\sY:(?P<y>[-]*\d+.\d+)\sZ:(?P<z>[-]*\d+.\d+)\sE:')
        m = re.search(regex,self.read_until(c=b"ok"))
        if len(m.groups()) == 3:
            self.x = float(m.group('x'))
            self.y = float(m.group('y'))
            self.z = float(m.group('z'))
            #print(f"X {self.x:.1f} | Y {self.y:.1f} | Z {self.z:.1f} | S {self.s:.1f}")
            #Two-digits precision for A350
            print(f"X {self.x:.2f} | Y {self.y:.2f} | Z {self.z:.2f} | X_S {self.x_s:.2f} | Y_S {self.y_s:.2f} | Z_S {self.z_s:.2f}")
            return self.x,self.y,self.z
        else:
            return self._serialport.timeout

    def check_limits(self, x,y,z, x_s,y_s,z_s):
        if self.limits["min_x"] <= x <= self.limits["max_x"]:
            self.x = x
        else:
            print(f"X out of bounds ({self.limits['min_x']:.2f} to {self.limits['max_x']:.2f})")
            
        if self.limits["min_y"] <= y <= self.limits["max_y"]:
            self.y = y
        else:
            print(f"Y out of bounds ({self.limits['min_y']:.2f} to {self.limits['max_y']:.2f})")
            
        if self.limits["min_z"] <= z <= self.limits["max_z"]:
            self.z = z
        else:
            print(f"Z out of bounds ({self.limits['min_z']:.2f} to {self.limits['max_z']:.2f})")
            
            
        if self.limits["min_s"] <= x_s <= self.limits["max_s"]:
            self.x_s = x_s
        else:
            print(f"Step x_s out of bounds ({self.limits['min_s']:.2f} to {self.limits['max_s']:.2f})")
            
        if self.limits["min_s"] <= y_s <= self.limits["max_s"]:
            self.y_s = y_s
        else:
            print(f"Step y_s out of bounds ({self.limits['min_s']:.2f} to {self.limits['max_s']:.2f})")
            
        if self.limits["min_s"] <= z_s <= self.limits["max_s"]:
            self.z_s = z_s
        else:
            print(f"Step z_s out of bounds ({self.limits['min_s']:.2f} to {self.limits['max_s']:.2f})")

    def manual(self):
        print("Entering Manual mode...")
        self.get_pos()
        while True:
            c = click.getchar()
            # ESC
            if c == '\x1b':
                click.echo('Exiting Manual mode...')
                break
            # Left Arrow
            elif c == '\x1b[D':
                new_x = self.x - self.x_s
                self.check_limits(new_x, self.y, self.z, self.x_s, self.y_s, self.z_s)
                self.set_pos(self.x, self.y, self.z)
            # Right Arrow
            elif c == '\x1b[C':
                new_x = self.x + self.x_s
                self.check_limits(new_x, self.y, self.z, self.x_s, self.y_s, self.z_s)
                self.set_pos(self.x, self.y, self.z)
            # Down Arrow
            elif c == '\x1b[B':
                new_y = self.y - self.y_s
                self.check_limits(self.x, new_y, self.z, self.x_s, self.y_s, self.z_s)
                self.set_pos(self.x, self.y, self.z)
            # Up Arrow
            elif c == '\x1b[A':
                new_y = self.y + self.y_s
                self.check_limits(self.x, new_y, self.z, self.x_s, self.y_s, self.z_s)
                self.set_pos(self.x, self.y, self.z)
            elif c == 'u':
                new_z = self.z + self.z_s
                self.check_limits(self.x, self.y, new_z, self.x_s, self.y_s, self.z_s)
                self.set_pos(self.x, self.y, self.z)
            elif c == 'd':
                new_z = self.z - self.z_s
                self.check_limits(self.x, self.y, new_z, self.x_s, self.y_s, self.z_s)
                self.set_pos(self.x, self.y, self.z)
            elif c == 's':
                try:
                    new_step = float(input("Enter desired step:"))
                    self.check_limits(self.x, self.y, self.z, new_step, new_step, new_step)
                except ValueError:
                    print("Steps value must be a float")
                    continue
            #This is a bit weired step increase/decrease
            # elif c == '+':
            #     if self.s < 1.0:
            #         self.s = 1.0
            #     elif self.s < 10.0:
            #         self.s = 10.0
            #     elif self.s < 100.0:
            #         self.s = 100.0
            # elif c == '-':
            #     if self.s >= 100.0:
            #         self.s = 10.0
            #     elif self.s >= 10.0:
            #         self.s = 1.0
            #     elif self.s >= 1.0:
            #         self.s = 0.1
            elif c == 'h':
                if input("!!! WARNING !!! Printer will go directly to X/Y origins (a.k.a. Home) without passing GO!\r\nEnsure that nothing is still on the bed\r\nContinue (y/n)?") == "y":
                    self.go_home_xy()
                else:
                    print("Canceled")
            elif c == 'z':
                if input("!!! WARNING !!! Printer will go directly to X/Y/Z origins without passing GO!\r\nEnsure that nothing is still on the bed\r\nContinue (y/n)?") == "y":
                    self.go_home_xyz()
                else:
                    print("Canceled")
            self.get_pos()
