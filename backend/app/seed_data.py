"""The Rebero - ALU route and its designated stops, in the order the bus visits them.

Coordinates were taken from Google Maps at the spot where the bus stops (Rebero -> ALU side).
Refine any of them after riding the route with the GPS test page from issue #9.
"""

ROUTE_NAME = "Rebero - ALU"

# (stop name, latitude, longitude), first stop going Rebero -> ALU first
STOPS: list[tuple[str, float | None, float | None]] = [
    ("Rebero", -1.9903207, 30.0612489),
    ("Rujugiro", -1.9852853, 30.075455),
    ("Kwa Kaboyi", -1.9796812, 30.0763949),
    ("Merez 2", -1.9749828, 30.0767511),
    ("Merez 1", -1.9704489, 30.0772722),
    ("SEGEM", -1.9660129, 30.0766136),
    ("Rwandex", -1.9693766, 30.086808),
    ("Sonatube", -1.9659055, 30.1032578),
    ("Remera Gare", -1.9587323, 30.1194352),
    ("Kimironko Gare", -1.9496424, 30.1252733),
    ("Kimironko Kwa Mushimire", -1.935076, 30.1338924),
    ("Zindiro", -1.9289174, 30.1393946),
    ("ALU Campus", -1.9299337, 30.1520531),
]
