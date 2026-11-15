"""The Rebero - ALU route and its designated stops, in the order the bus visits them.

Coordinates are still to be collected at each stop. Until a stop has both numbers,
the seed script refuses to run, so the map never shows a stop in the wrong place.
"""

ROUTE_NAME = "Rebero - ALU"

# (stop name, latitude, longitude), first stop going Rebero -> ALU first
STOPS: list[tuple[str, float | None, float | None]] = [
    ("Rebero", None, None),
    ("Rujugiro", None, None),
    ("Merez 2", None, None),
    ("Merez 1", None, None),
    ("SEGEM", None, None),
    ("Rwandex", None, None),
    ("Sonatube", None, None),
    ("Remera Gare", None, None),
    ("Kimironko Gare", None, None),
    ("Kimironko Kwa Mushimire", None, None),
    ("Zindiro", None, None),
    ("ALU Campus", None, None),
]
