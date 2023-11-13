#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from builtins import *
import dronekit_sitl, geocoder, time
from dronekit import connect

LAST_COORDINATES_FILE = "quadcopter_simulator_last_used_coordinates.txt"


def init_vehicle(lat=-1.0, lng=-1.0):
    paramsValid = False

    if lat != -1 or lng != -1:
        if not isinstance(lat, float):
            raise ValueError("lat is not a float")
        if not isinstance(lng, float):
            raise ValueError("lng is not a float")

        if lat == -1:
            raise ValueError("lat should be set")

        if lng == -1:
            raise ValueError("lng should be set")

        paramsValid = True

    # gives 3 tries for the reverse geocoding
    if not paramsValid:

        textAddress = ""

        reverseGeo = []

        g = geocoder.maxmind()
        reverseGeo.append((g.latlng, g.city + ", " + g.country))

        g = geocoder.ipinfo()
        reverseGeo.append((g.latlng, g.city + ", " + g.country))

        g = geocoder.freegeoip('')
        reverseGeo.append((g.latlng, g.city + ", " + g.country))

        optionChoosed = -1

        # read the file containing the last coordinates, if exists
        import os.path
        if os.path.isfile(LAST_COORDINATES_FILE):
            with open(LAST_COORDINATES_FILE) as f:

                l = [line.rstrip('\n') for line in f]

                # tests if the files is of the correct size
                if len(l) == 3:
                    lat, lng, textAddress = l
                    lat = float(lat)
                    lng = float(lng)

        print("Select the address that bests describes your current location")
        for i in range(3):
            print("Press", i + 1, "to choose :", reverseGeo[i][1])

        print("Press 4 to enter an address manually")
        print("Press 5 to enter the GPS coordinates manually")
        print("Press 6 to reuse the last used coordinates (" + textAddress + " : " + str(lat) + "," + str(lng) + ")")

        while optionChoosed not in range(1, 7):

            try:

                optionChoosed = int(input("\nPlease enter your choice :\n"))

                if 1 <= optionChoosed <= 3:
                    lat, lng = reverseGeo[optionChoosed - 1][0]

                elif optionChoosed == 4:

                    while True:
                        print("\tPlease enter a valid address (e.g. ICAM Bretagne, Vannes, France )")
                        textAddress = input("\t")  # for example ICAM Bretagne, Vannes, France
                        g = geocoder.google(textAddress)

                        time.sleep(1)
                        if g.ok:
                            lat = g.lat
                            lng = g.lng
                            break

                        else:
                            print("\tthe address is not valid")


                elif optionChoosed == 5:
                    print("\tPlease enter the latitude (e.g. 47.340082)")
                    lat = input("\t")
                    print("\tPlease enter the longitude (e.g. -2.878657)")
                    lng = input("\t")
                    textAddress = " "

                elif optionChoosed == 6:
                    pass




            except:
                print("[ERROR] - Please enter a valid choice")
                e = sys.exc_info()[0]
                print(e)
                optionChoosed = -1

        with open(LAST_COORDINATES_FILE, 'w') as the_file:
            the_file.write(str(lat) + '\n')
            the_file.write(str(lng) + '\n')
            the_file.write(unicode(textAddress))

    sitl = dronekit_sitl.start_default(lat=lat, lon=lng)
    connection_string = sitl.connection_string()

    # Connect to the Vehicle
    print('Connecting to vehicle on: %s' % connection_string)
    vehicle = connect(connection_string, wait_ready=True)

    return vehicle


'''

def test_init():

    print("~~~ PLEASE BE CAREFULL YOU ARE RUNNING THE TEST CASE !!! ~~~")


    vehicle = init_vehicle()


    input("Press ENTER key to interrupt...")

    vehicle.close()


test_init()
'''

if __name__ == '__main__':
    print("   /!\\    You are propably executing the wrong file  (" + __file__ + ")  !!!   /!\\   ", file=sys.stderr)