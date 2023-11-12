"""Topology of the network and related utilities."""
import json
from collections import OrderedDict
from math import log, sqrt
from pathlib import Path
from typing import Optional, cast
from functools import cache

from anyio import open_file
from async_lru import alru_cache
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
from geopy.location import Location as GeoLocation
from typer import get_app_dir


class Location:
    """Location (switch/city) in the topology."""
    def __init__(self, name: str, ip: str, index: int, population: int, lat, lon, link_count: int = 1) -> None:
        """Initialize a location object."""
        self.name = name
        self.index = index
        self.ip = ip
        self.ofname = f"of:{str(index+1).zfill(16)}"
        self.population = population
        self.lat = lat
        self.lon = lon
        self.link_count = link_count
    @property
    def coords(self) -> tuple[float, float]:
        """Get coordinates of a location."""
        return (self.lat, self.lon)


class Link:
    """Link between two locations (switches)."""
    def __init__(
            self, 
            locations: tuple[Location, Location], 
            distance: int, ports: Optional[tuple[int, int]] = None, 
            utilization: float = 0,
            ) -> None:
        """Initialize a link object."""
        self.locations = locations
        self.distance = distance
        self.ports = ports
        self.utilization = utilization
    @cache
    def delay_calc(self) -> float:
        """Calculate delay for a link."""
        return self.distance/200
    @cache
    def jitter_calc(self) -> float:
        """Calculate jitter (derivative of delay) for a link."""
        return log(sqrt(self.distance/200))
    @cache
    def bandwidth_calc(self) -> float:
        """Calculate bandwidth for a link."""
        return (
                (self.locations[0].population + 
                self.locations[1].population + 
                10*max(self.locations[0].population, self.locations[1].population)) / 9000000 - 
                self.distance / 3 + 
                (self.locations[0].link_count + self.locations[1].link_count) * 90
                )
    @cache
    def loss_calc(self) -> float:
        """Calculate loss for a link."""
        return (
                (self.locations[0].population + self.locations[1].population + 
                 max(self.locations[0].population, self.locations[1].population)) / 2000000000 + 
                self.distance / 1500000
                )
    @cache
    def port_to(self, location: Location) -> int:
        """Get the port number to a location."""
        if not self.ports:
            msg = "Ports not defined for link"
            raise ValueError(msg)
        return self.ports[1-self.locations.index(location)]
    
    def increase_utilization(self, amount: float) -> None:
        """Increase the utilization of a link."""
        self.utilization = min(self.bandwidth_calc(), self.utilization + amount)


class Topology:
    """Topology of the network."""
    def __init__(self, locations: list[Location] | None = None, links: list[Link] | None = None) -> None:
        """Initialize the topology."""
        self.locations: list[Location] = locations or []
        self.links: list[Link] = links or []
    def add_location(self, location: Location) -> None:
        """Add a new location to the topology."""
        self.locations.append(location)
    def add_link(self, link: Link) -> None:
        """Add a new link between locations to the topology."""
        self.links.append(link)
    def get_location(self, name: str) -> Location | None:
        """Get a location from the topology by name."""
        return next((location for location in self.locations if location.name == name), None)
    def get_link(self, l1: Location, l2: Location) -> Link | None:
        """Get a link between two locations (undirected)."""
        return next((link for link in self.links if l1 in link.locations and l2 in link.locations), None)
    def has_link(self, l1: Location, l2: Location):
        """Check if a link exists between two locations (undirected)."""
        return any(l1 in link.locations and l2 in link.locations for link in self.links)
    def port_to(self, src: Location, dst: Location):
        """Get the port number to a location."""
        return next(link.port_to(dst) for link in self.links if src in link.locations and dst in link.locations)

@alru_cache(maxsize=64)
async def get_geo(name: str) -> GeoLocation | None:
    """Get geolocation by name of a place (e.g. city)."""
    async with Nominatim(user_agent="scht_lab_pw", adapter_factory=AioHTTPAdapter) as geolocator:
        coro = geolocator.geocode(name, exactly_one=True)
        if coro is None:
            return None
        return cast(GeoLocation, await coro)

async def load_topology(topo_data: OrderedDict[str, OrderedDict[str, int | OrderedDict[str, int]]]) -> Topology:
    """Load topology from a OrderedDict."""
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
        ))

    
    for city in topo_data.keys():
        city_location = topo.get_location(city)
        for neighbor in cast(OrderedDict, topo_data[city]["neighbors"]).keys():
            neighbor_location = topo.get_location(neighbor)
            if city_location is None or neighbor_location is None or topo.has_link(city_location, neighbor_location):
                continue
            city_location.link_count += 1
            neighbor_location.link_count += 1
            topo.add_link(
                Link(
                    (city_location, neighbor_location),
                    cast(int, cast(OrderedDict, topo_data[city]["neighbors"])[neighbor]),
                    ports=(city_location.link_count, neighbor_location.link_count),
                ),
            )
    return topo

async def load_topology_from_file(filename: str | Path) -> Topology:
    """Load topology from a file."""
    async with await open_file(filename, "r") as f:
        data = await f.read()
        return await load_topology(json.loads(data, object_pairs_hook=OrderedDict))


async def default_topo() -> Topology:
    """Load the default topology (from app directory)."""
    path = Path(get_app_dir("scht_lab")) / "topo.json"
    topo = await load_topology_from_file(path)
    return topo
