import printer
import chip 
import time
import click

# target = chip.chip()

# # origin
# target.set_home(-150,167)

# # chip definition
# target.set_end(-148,169)

# # steps
# target.steps = 0.2



    
    
    
# Define Serial port settings
serial_port = "/dev/ttyUSB0" # or set to None for automatic detection
serial_baud = 115200
serial_timeout = 1

# Establish connection with the printer
p = printer.printer(port=serial_port,baudrate=serial_baud, timeout=serial_timeout)

# Load printer limits definitions from configuration file
p.load_settings("settings/a350.ini")

# Enter Manual mode


# time.sleep(1)

# 


# p.acc_rates()

# p.get_config()
p.get_pos()

print(p.x, p.y, p.z, p.x_s, p.y_s, p.z_s)

p.manual()



# for position in target.horizontal():
#     print(position)
        
# p.spindle_on()
# while True:    
   
#     for position in target.horizontal():

#         p.check_limits(position[0], position[1], p.z, p.s)
#         p.set_pos(position[0], position[1], p.z)
        
#         # time.sleep(0.1)
    
#     time.sleep(0.1)
    
#     c = click.getchar()
#     # ESC
#     if c == '\x1b':
#         p.spindle_off()
#         break
    
#     elif c == 'd':
#         new_z = p.z - p.s
#         p.check_limits(p.x, p.y, new_z, p.s)
#         p.set_pos(p.x, p.y, new_z)
        
# p.spindle_off()
    

