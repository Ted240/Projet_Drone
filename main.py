import geocoder
import math
import json
# pathdict is mandatory for script to run, auto install later on

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
        _in = input(f"{request} [{prompt_poss}] ")
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
        print(request)
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
        with open(self._path, "r") as f:
            self._content = pathdict.PathDict(json.load(f), create_if_not_exists=True)

    def save(self):
        with open(self._path, "w+") as f:
            json.dump(self._content.data, f, default=lambda x: x.data if isinstance(x, (pathdict.PathDict, pathdict.collection.StringIndexableList)) else x, indent=2)

    def __getitem__(self, item):
        return self._content[item]

    def __setitem__(self, key, value):
        self._content[key] = value



def get_address(addr, log=False):
    g = geocoder.osm(addr)
    if g.ok:
        return g
    else:
        if log: print(f"\33[33m[!] L'adresse '{addr}' n'a pas été trouvé\33[0m")
        return

def ask_addresses():
    """
    Ask addresses to visit

    :return: Addresses array
    """
    _return = []
    while True:
        _in = input("Entrez une adresse [Vide pour valider]:\n>>> ")
        if _in == "": break
        _return.append(_in)
    return _return

def convert_latlon(addresses_list):
    """
    Map geolocation from addresses array

    :param addresses_list: Addresses to search for
    :return: Geolocation coordinates found
    """
    return [a for a in [get_address(addr, True).latlng for addr in addresses_list] if a]

def ask_starting_geo():
    """
    Ask starting drone location
    Available selection:
    - Geolocation
    - Manual input
    - History
    - Saved

    :return: Starting point lat/lng
    """
    addr_saved = config["location.start.saved"]
    addr_history = config["location.start.history"]
    # for addr, coords in addr_saved.items():
    #     choices.append(f"{addr} ({', '.join(map(str, coords))})")
    # for addr, coords in addr_history.items():
    #     choices.append(f"{addr} ({', '.join(map(str, coords))})")
    choice = pick_choice(
        "Point de départ",
        ["", ["Localisation automatique", "Entrée manuelle"]],
        ["Sauvegardées", [f"{addr:<40} ({','.join(map('{:^8.3f}'.format, coords))})" for addr, coords in addr_saved]],
        ["Historique", [f"{addr:<40} ({','.join(map('{:^8.3f}'.format, coords))})" for addr, coords in addr_history]]
    )
    print(choice)
    def save_historic(name, loc):
        print(name)
        # Already in historic ?
        loc_names = [x[0] for x in config["location.start.history"]]
        if name in loc_names:
            # True, remove older to then add a new one on top
            config["location.start.history"].remove([name, loc])
        # Add on top
        config["location.start.history"].insert(0, [name, loc])
        # If too many elements, remove the older one
        if len(config["location.start.history"]) > config["config.max_history"]:
            config["location.start.history"] = config["location.start.history"][:config["config.max_history"]]
        config.save()
    if choice["global_i"] == 0: # Auto-location
        g = geocoder.ipinfo()
        if y_n_choices(f"Choisir cette adresse ? {g.city if g.city else g.village} - {g.country} ({','.join(map('{:^8.3f}'.format, g.latlng))})"):
            save_historic(f"{g.city if g.city else g.village} - {g.country}", g.latlng)
            return g.latlng
    if choice["global_i"] == 1: # Manual entry
        while True:
            g = get_address(input("Adresse\n>>> "), True)
            if g:
                save_historic(f"{g.city if g.city else g.village} - {g.country}", g.latlng)
                return g.latlng
    # Already known addresses (saved or historic)
    return [*(addr_saved if choice["section_i"] == 1 else addr_history)][choice["index"]][1]

# Trying pathdict module importation
try:
    # noinspection PyUnresolvedReferences
    import pathdict
except ModuleNotFoundError:
    # 'pathdict' module not found, asking installation
    if y_n_choices("Le module python 'pathdict' n'est actuellement pas installé sur cette version de python, voulez vous l'installer", default=False):
        # Install
        import sys
        import os
        python_path = sys.executable
        os.system(f'"{python_path}" -m pip install pathdict')
        # noinspection PyUnresolvedReferences
        import pathdict
    else:
        # Abandon de l'installation
        print("Opération abandonnée. Le programme n'a pas pu continuer")
        exit(1)

if __name__ == '__main__':
    config = JSONFile("config.json")
    print(ask_starting_geo())
    # addresses = ask_addresses()
    # print(convert_latlon(addresses))
