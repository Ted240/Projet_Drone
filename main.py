import geocoder
import math
import json

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

def get_address(addr, log=False):
    g = geocoder.osm(addr)
    if g.ok:
        return g
    else:
        if log: print(f"\33[33m[!] L'adresse '{addr}' n'a pas été trouvé\33[0m")
        return False

def ask_addresses():
    """
    Demande les adresses à faire visiter au drone

    :return: Liste des adresses
    """
    _return = []
    while True:
        _in = input("Entrez une adresse [Vide pour valider]:\n>>> ")
        if _in == "": break
        _return.append(_in)
    return _return

def convert_latlon(addresses_list):
    """
    Convertie la liste d'adresses en coordonnés satellites

    :param addresses_list: Liste des adresses à chercher
    :return: Coordonnés GPS trouvées
    """
    return [a for a in [get_address(addr, True).latlng for addr in addresses_list] if a]

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
        g = geocoder.ipinfo()
        if y_n_choices(f"Choisir cette adresse ? {g.city} - {g.country} ({', '.join(g.latlng)})"):
            return g
    if choice == 1: # Manual entry
        while True:
            g = get_address(input("Adresse\n>>> "), True)




if __name__ == '__main__':
    ask_starting_geo()
    addresses = ask_addresses()
    print(convert_latlon(addresses))
