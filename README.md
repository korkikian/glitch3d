# Glitch3d #
**THIS MODULE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND**

This module offers basic functions to drive a 3D Marlin compatible printer through USB (e.g. to perform FI attacks).

The master branch will be kept as generic as possible.

Some printers may not behave identically, therefore branches with specific settings are available for fundamental differences.

The module has been tested on the following models:
- Creality Ender3 (ender3)
- Creality 6 SE (6se)

## Example code for CR-6 SE##
```
from glitch3d import printer

# Define Serial port settings
serial_port = "/dev/ttyUSB0" # or set to None for automatic detection
serial_port = None 
serial_baud = 115200
serial_timeout = 1

# Establish connection with the printer
p = printer(port=serial_port,baudrate=serial_baud, timeout=serial_timeout)

# Define printer bed limits (mm)
p.limits["min_x"] = 0.0
p.limits["max_x"] = 235.0
p.limits["min_y"] = 0.0
p.limits["max_y"] = 235.0
p.limits["min_z"] = 0.0
p.limits["max_z"] = 250.0
p.limits["min_s"] = 0.1
p.limits["max_s"] = 100.0

# Enter Manual mode
p.manual()

```

## Manual mode ##
In Manual mode, the following keystrokes are supported:

* `up` Move probe forward / Y + step
* `down` Move probe forward / Y - step
* `right` Move probe right / X + step
* `left` Move probe left / X - step 
* `u` Raise probe / Z + step
* `d` Lower probe / Z - step
* `+` Increase step (0.1,1,10,100)
* `-` Decrease step (100,10,1,0.1)
* `s` Manual step definition
* `h` Home on XY !!! WARNING printer dependant
* `z` Home on XYZ 

For safety reasons, a small routine was added to raise the probe of 20.0 mm before homing.
