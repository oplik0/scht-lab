import json
from collections import OrderedDict
from math import log, sqrt
from pathlib import Path
from typing import Optional, Union, cast
from geopy.geocoders import Nominatim
from geopy.location import Location as GeoLocation
from geopy.adapters import AioHTTPAdapter
from async_lru import alru_cache
from typer import get_app_dir

from anyio import open_file
from contextlib import asynccontextmanager
    

class Location():
    def __init__(self, name: str, ip: str, index: int, population: int, lat, lon, link_count: int) -> None:
        self.name = name
        self.index = index
        self.ip = ip
        self.ofname = f"of:{str(index+1).zfill(16)}"
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
    def __init__(self, locations: Optional[list[Location]] = None, links: Optional[list[Link]] = None) -> None:
        self.locations: list[Location] = locations or []
        self.links: list[Link] = links or []
    def add_location(self, location: Location) -> None:
        self.locations.append(location)
    def add_link(self, link: Link) -> None:
        self.links.append(link)
    def get_location(self, name: str) -> Optional[Location]:
        return next((location for location in self.locations if location.name == name), None)
    def has_link(self, l1: Location, l2: Location):
        return any(l1 in (link.src, link.dst) and l2 in (link.src, link.dst) for link in self.links)

@alru_cache(maxsize=64)
async def get_geo(name: str) -> GeoLocation | None:
    async with Nominatim(user_agent="scht_lab_pw", adapter_factory=AioHTTPAdapter) as geolocator:
        coro = geolocator.geocode(name, exactly_one=True)
        assert coro is not None
        return cast(GeoLocation, await coro)

async def load_topology(topo_data: OrderedDict[str, OrderedDict[str, int | OrderedDict[str, int]]]) -> Topology:
    """
    Load topology from a OrderedDict and return a graph object.
    """
    topo = Topology()
    topo_index = lambda x: list(topo_data.keys()).index(x)
    for city in topo_data.keys():
        location = await get_geo(city)
        index = topo_index(city)
        topo.add_location(Location(
            name=city,
            ip=f"10.0.0.{index+1}/8",
            index=index,
            population=cast(int, topo_data[city]["population"]),
            lat=location.latitude if location else 0,
            lon=location.longitude if location else 0,
            link_count=len(cast(OrderedDict, topo_data[city]["neighbors"]))
        ))

    
    for city in topo_data.keys():
        city_location = topo.get_location(city)
        for neighbor in cast(OrderedDict, topo_data[city]["neighbors"]).keys():
            neighbor_location = topo.get_location(neighbor)
            if city_location is None or neighbor_location is None or topo.has_link(city_location, neighbor_location):
                continue
            
            topo.add_link(
                Link(
                    city_location,
                    neighbor_location,
                    cast(int, cast(OrderedDict, topo_data[city]["neighbors"])[neighbor])
                )
            )
    return topo

async def load_topology_from_file(filename: str | Path) -> Topology:
    async with await open_file(filename, "r") as f:
        data = await f.read()
        return await load_topology(json.loads(data, object_pairs_hook=OrderedDict))


async def default_topo() -> Topology:
    path = Path(get_app_dir("scht_lab")) / "topo.json"
    topo = await load_topology_from_file(path)
    return topo
