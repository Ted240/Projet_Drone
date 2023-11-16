import geocoder
import math
import json

def y_n_choices(request, default = None):
    """
    Ask user choice between yes or no
    Default can be specified
    :param request: Input text printed as question
    :param default: [None/y/n]
    :return:
    """

def pick_choice(request, *args):
    """
    Ask user choice between multiple possibilities.
    Prevent OOB inputs

    :param request: Input text printed as question
    :param args: Possibilities description
    :return: Chosen possibility index
    """
    # Automatic return if one possibility is available
    if len(args) == 1:
        return 0

    # Asking loop
    line = "{i:<" + str(math.floor(math.log10(len(args)))) + "} - {poss}"
    while True:
        print(request)
        print("\n".join(
            [line.format(i=i+1, poss=poss) for i, poss in enumerate(args)]
        ))
        _in = input(">>> ")
        _in = _in.strip(" ").strip("\n")  # Remove exceeding chars
        # VERIFICATION
        # Input is not a number
        if not _in.isnumeric():
            continue
        _in = int(_in)
        # Input is in range
        if 1 <= _in <= len(args):
            return _in - 1
        # Else restart loop

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
    :return: Geolocation coordonates found
    """
    return [geocoder.osm(address).latlng for address in addresses_list]

def ask_starting_geo():
    """
    Ask starting drone location
    Available selection:
    - History
    - Geolocation
    - Manual input

    :return: Starting point lat/lng
    """
    choices = ["Localisation automatique", "Entrée manuelle"]
    [choices.append(f"Historique * {x}") for x in json.load(open("config.json", "r")).get("history", {}).get("start", [])]
    choice = pick_choice("Point de départ", *choices)
    if choice == 0: # Auto-location
        choices = map(lambda g: f"{g.city} - {g.country} ({g.latlng})", [geocoder.ipinfo(), geocoder.freegeoip("")])
        pick_choice("Quelle position est la plus proche ?", *choices)


if __name__ == '__main__':
    ask_starting_geo()
    addresses = ask_addresses()
    print(convert_latlon(addresses))
