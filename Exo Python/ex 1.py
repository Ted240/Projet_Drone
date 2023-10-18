from math import pi
r, h = tuple(map(float, [input(f"{x}: ") for x in ["Radius", "Height"]]))
print(f"Volume = {(pi * r**2 * h) / 3.0}")