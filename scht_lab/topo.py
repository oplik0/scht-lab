import json
from collections import OrderedDict
from math import log, sqrt
from typing import Optional




def load_topology():
    """
    Load topology from a OrderedDict and return a graph object.
    """
    

class Location():
    def __init__(self, name: str, ip: str, index: int, population: int, lat, lon, link_count: int) -> None:
        self.name = name
        self.ip = ip
        self.index = index
        self.ofname = f"of:{str(index).zfill(16)}"
        self.population = population
        self.lat = lat
        self.lon = lon
        self.link_count = link_count


class Link():
    def __init__(self, src: Location, dst: Location, distance: int) -> None:
        self.src = src
        self.dst = dst
        self.distance = distance
    def delay_calc(self) -> float:
        return self.distance/200

    def jitter_calc(self) -> float:
        return log(sqrt(self.distance/200))

    def bandwidth_calc(self) -> float:
        return (self.src.population + self.dst.population + 10*max(self.src.population, self.dst.population)) / 9000000 - self.distance / 3 + (self.src.link_count + self.dst.link_count) * 90

    def loss_calc(self) -> float:
        return (self.src.population + self.dst.population + max(self.src.population, self.dst.population)) / 2000000000 + self.distance / 1500000



class Topology():
    def __init__(self, locations: Optional[list[Location]], links: Optional[list[Link]]) -> None:
        self.locations: list[Location] = locations or []
        self.links: list[Link] = links or []
