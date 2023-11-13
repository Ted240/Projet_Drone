from __future__ import print_function
from builtins import *

#import the needed function from the quadcopter_simulator.py file
from quadcopter_simulator import init_vehicle


print("Starting simulator...")

# Connect to the Vehicle, located at the asked coordinates (47.6897121 , -2.7478361)
vehicle = init_vehicle(47.6897121, -2.7478361)

# Get some vehicle attributes (state)
print("Get some vehicle attribute values:")
print(" GPS: %s" % vehicle.gps_0)
print(" Battery: %s" % vehicle.battery)
print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
print(" Is Armable?: %s" % vehicle.is_armable)
print(" System status: %s" % vehicle.system_status.state)
print(" Mode: %s" % vehicle.mode.name) # settable

# Close vehicle object before exiting script
vehicle.close()

# end of the program
print("Completed")