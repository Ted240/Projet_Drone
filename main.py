"""
PROJET DRONE

Python 3.8
"""

import math, json, time, os

# Enable color in console
os.system("color")

# pathdict is mandatory for script to run, auto install later on
# geocoder is mandatory for script to run, auto install later on
# requests is mandatory for script to run, auto install later on
# dronekit_sitl is mandatory for script to run, auto install later on
# dronekit is mandatory for script to run, auto install later on
# pymavlink is mandatory for script to run, auto install later on
import dronekit_wrapper

"""
Import pathdict

Handle path for dictionaries
"""
try:
    import pathdict
except ModuleNotFoundError:
    dronekit_wrapper.install_package("pathdict")
    import pathdict

"""
Import geocoder

Addresses geolocation
"""
try:
    import geocoder
except ModuleNotFoundError:
    dronekit_wrapper.install_package("geocoder")
    import geocoder

def y_n_choices(request, default = None):
    """
    Ask user choice between yes or no
    Default can be specified
    :param request: Input text printed as question
    :param default: [None/y/n]
    :return: True for yes and False for no
    """
    y, n = "y", "n"
    prompt_poss = {"None": f"{y}/{n}", "True": f"\33[4m{y}\33[0m/{n}", "False": f"{y}/\33[4m{n}\33[0m"}[str(default if default in [None, False, True] else None)]
    while True:
        _in = input(f"\n\n\33[1m{request}\33[0m [{prompt_poss}] ")
        _in = _in.strip(" ").strip("\n")
        if _in.lower() in ["y", "yes", "oui", "o", "1"]: return True
        if _in.lower() in ["no", "non", "n", "0"]: return False
        if default is not None and _in == "": return default
        print("\33[31mInvalid input\33[0m")

def pick_choice(request, *sections, empty_section=False):
    """
    Ask user choice between multiple possibilities.
    Prevent OOB inputs

    :param request: Input text printed as question
    :param sections: Sections definition ( [{%label% = [%choices%]}, ... ] )
    :param empty_section: True to keep section even if it's empty
    :return: Chosen possibility as {global-index, section-index, list, index, text}
    """
    # Array flattening
    args = [i for sec in sections for i in sec[1]]
    # Automatic return if one possibility is available
    if len(args) == 1:
        return {
            "global_i": 0,
            "section_i": 0,
            "list": sections[0],
            "index": 0,
            "text": sections[0][0]
        }
    # Asking loop
    section = "{label:─^50}", "[ %label% ]"
    line = "{i:<" + str(math.floor(math.log10(len(args)))) + "} * {poss}"
    while True:
        choices_map = []
        # Print request
        print(f"\n\n\33[1m{request}\33[0m")
        # Print all possibilities
        # Print sections
        for s_index, _s_values in enumerate(sections):
            s_name, s_values = _s_values
            if s_name != "" and (len(s_values) or empty_section): # Show section name if it's defined and section is filled or `remove_empty` is disabled
                print(section[0].format(label=section[1].replace("%label%", s_name)))
            for c_index, c_text in enumerate(s_values):
                choices_map.append([s_index, c_index])
                print(line.format(i=len(choices_map), poss=c_text))
        # User prompt
        _in = input(">>> ")
        _in = _in.strip(" ").strip("\n")  # Remove exceeding chars
        # VERIFICATION
        # Input is not a number
        if not _in.isnumeric():
            continue
        _in = int(_in)
        # Input is in range
        if 1 <= _in <= len(args):
            # Return formatted fields
            return {
                "global_i": _in - 1,
                "section_i": choices_map[_in-1][0],
                "list": sections[choices_map[_in-1][0]][1],
                "index": choices_map[_in-1][1],
                "text": sections[choices_map[_in-1][0]][1][choices_map[_in-1][1]]
            }
        # Else restart loop

class JSONFile:
    """
    JSON File object
    Make json file management and edition easier
    """
    def __init__(self, path):
        self._path = path
        self._content = pathdict.PathDict({})
        self._open()
        self.refresh = self._open
        self.get = self.__getitem__
        self.set = self.__setitem__

    @property
    def path(self): return self._path

    def _open(self):
        """
        Open the file, create it if not existing
        """
        if not os.path.exists(self._path):
            print(f"Configuration file '{self._path}' is missing and has to be created")
            if y_n_choices(f"Le fichier de configuration '{self._path}' est absent et doit être créer\nVoulez vous importer le fichier directement depuis GitHub ?", True):
                """
                Import requests

                Configuration file fetching
                """
                try:
                    import requests as req
                except ModuleNotFoundError:
                    dronekit_wrapper.install_package("requests")
                    import requests as req
                # noinspection PyBroadException
                try:
                    self._content = pathdict.PathDict(req.get("https://raw.githubusercontent.com/Ted240/Projet_Drone/master/config.json").json())
                except:
                    print("Une erreur s'est produite, les valeurs par défaut vont être utilisées")
            if self._content.data == {}:
                self._content = pathdict.PathDict({"location":{"saved": [],"history": []},"config": {"max_history": 5}})
            self.save()
            print(f"Fichier '{self._path}' créé")
        with open(self._path, "r") as f:
            self._content = pathdict.PathDict(json.load(f), create_if_not_exists=True)

    def save(self):
        """
        Save the file
        """
        with open(self._path, "w+") as f:
            json.dump(self._content.data, f, default=lambda x: x.data if isinstance(x, (pathdict.PathDict, pathdict.collection.StringIndexableList)) else x, indent=2)

    def __getitem__(self, item):
        return self._content[item]

    def __setitem__(self, key, value):
        self._content[key] = value



def get_address(address, log=False):
    """
    Return geolocation object if address found
    :param address:
    :param log:
    :return:
    """
    g = geocoder.osm(address)
    if g.ok:
        return g
    else:
        if log: print(f"\33[33m[!] L'adresse '{address}' n'a pas été trouvé\33[0m")
        return

def ask_geo(request_title):
    """
    Ask starting drone location
    Available selection:
    - Geolocation
    - Manual input
    - History
    - Saved

    :param request_title: Question to ask user
    :return: Starting point lat/lng
    """

    def generate_gmaps_link(geo):
        """
        Return Google Maps link to the address
        :param geo: Geolocated address
        :return: Google Maps link
        """
        return f"https://www.google.fr/maps/search/{geo.latlng[0]},{geo.latlng[1]}"

    def get_city_name(geo):
        """
        Return address name
        :param geo: Address geolocation
        :return: Address name
        """
        geo: geocoder.api.OsmQuery
        if geo.city is not None: return geo.city
        if geo.town is not None: return geo.town
        if geo.village is not None: return geo.village
        if geo.municipality is not None: return geo.municipality
        if geo.district is not None: return geo.district
        if geo.neighborhood is not None: return geo.neighborhood
        if geo.quarter is not None: return geo.quarter

    def get_location_name(geo):
        """
        Return address name
        :param geo: Address geolocation
        :return: Address name
        """
        return f"{'' if geo.street is None else f'{geo.street} - '}{get_city_name(geo)} - {geo.country}"

    def save_historic(name, loc):
        """
        Save an address under a name
        :param name: Friendly name
        :param loc: Location
        """
        # print(name)
        # Already in historic ?
        loc_names = [x[0] for x in config["location.history"]]
        if name in loc_names:
            # True, remove older to then add a new one on top
            config["location.history"].remove([name, loc])
        # Add on top
        config["location.history"].insert(0, [name, loc])
        # If too many elements, remove the older one
        if len(config["location.history"]) > config["config.max_history"]:
            config["location.history"] = config["location.history"][:config["config.max_history"]]
        config.save()

    # Get all saved addresses and ask user
    while True:
        addr_saved = config[f"location.saved"]
        addr_history = config[f"location.history"]
        choice = pick_choice(
            request_title,
            ["", ["Localisation automatique", "Entrée manuelle"]],
            ["Sauvegardées", [f"{address:<40} ({','.join(map('{:^8.3f}'.format, coords))})" for address, coords in addr_saved]],
            ["Historique", [f"{address:<40} ({','.join(map('{:^8.3f}'.format, coords))})" for address, coords in addr_history]]
        )

        if choice["global_i"] == 0: # Auto-location
            g = geocoder.ipinfo()
            if y_n_choices(f"Choisir cette adresse ? {get_location_name(g)} ({','.join(map('{:^8.3f}'.format, g.latlng))}) [{generate_gmaps_link(g)}"):
                save_historic(get_location_name(g), g.latlng)
                return g.latlng
        if choice["global_i"] == 1: # Manual entry
            while True:
                g = get_address(input("Adresse\n>>> "), True)
                if g:
                    if y_n_choices(f"Choisir cette adresse ? {get_location_name(g)} ({','.join(map('{:^8.3f}'.format, g.latlng))}) [{generate_gmaps_link(g)}]"):
                        save_historic(get_location_name(g), g.latlng)
                        return g.latlng
        if choice["global_i"] > 1: # Already known addresses (saved or historic)
            address = [*(addr_saved if choice["section_i"] == 1 else addr_history)][choice["index"]]
            if choice["section_i"] != 1: save_historic(*address)
            return address

if __name__ == '__main__':
    # Load config file
    config = JSONFile("config.json")
    start = ask_geo("Entrez un point de départ")
    addresses = []
    while True:
        addresses.append(ask_geo("Entrez un point à visiter"))
        if not y_n_choices("Ajouter un autre point ?", default=False):
            break
    # Create drone at home location
    print(start)
    drone = dronekit_wrapper.Drone(start[1][0], start[1][1], "127.0.0.1")
    # Drone takeoff
    drone.arm_and_takeoff(20)
    # Mission creation, addresses assignment
    drone.create_mission()
    for addr in addresses:
        drone.add_waypoint(addr[0], addr[1])
    # Mission start
    drone.start_mission()

    # Drone is going to an address
    while not drone.is_returning:
        print(f"\n[Target {drone.vehicle.commands.next}]\n  Distance: {drone.waypoint_distance:.1f}m\n  Altitude: {drone.location[2]:.2f}m")
        time.sleep(1)

    # Drone is going back to home
    while not drone.has_finished:
        print(f"\n[Back to Home]\n  Distance: {drone.home_distance:.1f}m\n  Altitude: {drone.location[2]:.2f}m")
        time.sleep(1)
    drone.land()

    # Drone is landing
    while drone.location[2] > .1:
        print(f"\n[Back to home]\n  Distance: {drone.home_distance:.1f}m\n  Altitude: {drone.location[2]:.2f}m")
        time.sleep(1)

    # Stopping drone
    drone.stop()
    print("Drone posé")
    os.system("pause")

