"""Topology of the network and related utilities."""
from asyncio import gather
import json
from collections import OrderedDict
from math import log, sqrt
from pathlib import Path
import time
from typing import Optional, cast, Awaitable
from functools import cache
from ipaddress import ip_interface, IPv4Interface, IPv6Interface

from anyio import open_file
from aiocache import cached
from aiocache.serializers import MsgPackSerializer
from aiofilecache import FileCache

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim, Photon, IGNFrance, DataBC
from geopy.location import Location as GeoLocation
from geopy.exc import GeopyError
from typer import get_app_dir
from scht_lab.helpers.gather_dict import gather_dict
from scht_lab.helpers.location_serializer import LocationSerializer

from scht_lab.models.flow import Flow, Selector, Treatment
from scht_lab.models.topo import Topology as TopologyModel
from rich import print

class Location:
    """Location (switch/city) in the topology."""
    def __init__(self, name: str, ip: str | IPv4Interface | IPv6Interface, index: int, population: int, lat: Optional[int] = None, lon: Optional[int] = None, link_count: int = 1) -> None:
        """Initialize a location object."""
        self.name = name
        self.index = index
        if isinstance(ip, str):
            self.ip = ip_interface(ip)
        else:
            self.ip = ip
        self.ofname = f"of:{hex(index+1)[2:].zfill(16)}"
        self.population = population
        self.lat = lat
        self.lon = lon
        self.link_count = link_count
    
    def set_geo(self, geo: GeoLocation) -> None:
        """Set coordinates of a location."""
        self.lat = geo.latitude
        self.lon = geo.longitude
    @property
    def coords(self) -> tuple[float, float]:
        """Get coordinates of a location."""
        if self.lat is None or self.lon is None:
            raise ValueError("Location does not have coordinates")
        return (self.lat, self.lon)
    def endpoint_flows(self) -> list[Flow]:
        return [
            Flow(
                deviceId=self.ofname,
                isPermanent=True,
                priority=65534,
                timeout=0,
                selector=Selector(
                    criteria=[
                        {
                            "type": "ETH_TYPE",
                            "ethType": "0x800" if self.ip.version == 4 else "0x86dd",
                        },
                        {
                            "type": "IPV4_DST" if self.ip.version == 4 else "IPV6_DST",
                            "ip": f"{self.ip.ip}/{self.ip.max_prefixlen}",
                        } # type: ignore
                    ]
                ),
                treatment=Treatment(
                    instructions=[
                        {
                            "type": "OUTPUT",
                            "port": "1",
                        }
                    ]
                ),
            ),
        ]
    def __rich_repr__(self):
        yield "name", self.name
        yield "ip", self.ip
        yield "index", self.index
        yield "ofname", self.ofname
        yield "population", self.population
        yield "lat", self.lat, None
        yield "lon", self.lon, None
        yield "link_count", self.link_count

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
                (
                    self.locations[0].population + 
                    self.locations[1].population + 
                    10*max(self.locations[0].population, self.locations[1].population)
                ) / 80000 - 
                self.distance / 8
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
    def __rich_repr__(self):
        yield "locations", self.locations
        yield "distance", self.distance
        yield "ports", self.ports
        yield "utilization", self.utilization
        yield "delay", self.delay_calc()
        yield "jitter", self.jitter_calc()
        yield "bandwidth", self.bandwidth_calc()
        yield "loss", self.loss_calc()

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
        ip = IPv4Interface("0.0.0.0/0")
        try:
            ip = ip_interface(name)
        except ValueError:
            pass
        return next((location for location in self.locations if location.name == name or ip.ip == location.ip.ip), None)
        
    def get_link(self, l1: Location, l2: Location) -> Link | None:
        """Get a link between two locations (undirected)."""
        return next((link for link in self.links if l1 in link.locations and l2 in link.locations), None)
    def has_link(self, l1: Location, l2: Location):
        """Check if a link exists between two locations (undirected)."""
        return any(l1 in link.locations and l2 in link.locations for link in self.links)
    def port_to(self, src: Location, dst: Location):
        """Get the port number to a location."""
        return next(link.port_to(dst) for link in self.links if src in link.locations and dst in link.locations)

    @property
    @cache
    def max_delay(self) -> float:
        """Get the maximum delay in the topology."""
        return max(link.delay_calc() for link in self.links)
    @property
    @cache
    def max_jitter(self) -> float:
        """Get the maximum jitter in the topology."""
        return max(link.jitter_calc() for link in self.links)
    @property
    @cache
    def max_bandwidth(self) -> float:
        """Get the maximum bandwidth in the topology."""
        return max(link.bandwidth_calc() for link in self.links)
    @property
    @cache
    def max_loss(self) -> float:
        """Get the maximum loss in the topology."""
        return max(link.loss_calc() for link in self.links)
    def __rich_repr__(self):
        yield "locations", self.locations
        yield "links", self.links

@cached(serializer=LocationSerializer(), cache=FileCache, basedir=Path(get_app_dir("scht_lab")) / "cache")
async def get_geo(name: str) -> GeoLocation | None:
    """Get geolocation by name of a place (e.g. city)."""
    for provider in [Nominatim, Photon, IGNFrance, DataBC]:
        async with provider(user_agent="scht_lab_pw", adapter_factory=AioHTTPAdapter) as geolocator:
            coro = geolocator.geocode(name, exactly_one=True)
            if coro is None:
                return None
            try:
                return cast(GeoLocation, await coro)
            except GeopyError:
                continue
async def load_topology(topo_data: OrderedDict[str, OrderedDict[str, int | OrderedDict[str, int]]]) -> Topology:
    """Load topology from a OrderedDict."""
    topo = Topology()
    topo_index = lambda x: list(topo_data.keys()).index(x)
    city_geo_lookups: dict[Location, Awaitable[GeoLocation | None]] = {}
    for city in topo_data.keys():
        index = topo_index(city)
        city_data = Location(
            name=city,
            ip=f"10.0.0.{index+1}/8",
            index=index,
            population=cast(int, topo_data[city]["population"])
        )
        city_geo_lookups[city_data] = get_geo(city)
        topo.add_location(city_data)

    
    for city in topo_data.keys():
        city_data = topo.get_location(city)
        for neighbor in cast(OrderedDict, topo_data[city]["neighbors"]).keys():
            neighbor_location = topo.get_location(neighbor)
            if city_data is None or neighbor_location is None or topo.has_link(city_data, neighbor_location):
                continue
            city_data.link_count += 1
            neighbor_location.link_count += 1
            topo.add_link(
                Link(
                    (city_data, neighbor_location),
                    cast(int, cast(OrderedDict, topo_data[city]["neighbors"])[neighbor]),
                    ports=(city_data.link_count, neighbor_location.link_count),
                ),
            )
    geo_data = await gather_dict(city_geo_lookups)
    for city, geo in geo_data.items():
        if city is not None and geo is not None:
            city.set_geo(geo)
    return topo

async def load_topology_from_file(filename: str | Path) -> Topology:
    """Load topology from a file."""
    async with await open_file(filename, "r") as f:
        data = await f.read()
        topo_data = json.loads(data, object_pairs_hook=OrderedDict)
        return await load_topology(topo_data)


async def default_topo() -> Topology:
    """Load the default topology (from app directory)."""
    path = Path(get_app_dir("scht_lab")) / "topo.json"
    topo = await load_topology_from_file(path)
    return topo

def to_model(topo: Topology) -> TopologyModel:
    """Convert a Topology object to a TopologyModel."""
    data = {location.name: {"population": location.population, "neighbors": {}} for location in topo.locations}
    for link in topo.links:
        data[link.locations[0].name][link.locations[1].name] = link.distance
        data[link.locations[1].name][link.locations[0].name] = link.distance
    return TopologyModel.model_validate(data)

async def save_default(topo: TopologyModel | Topology) -> None:
    """Save the default topology (to app directory)."""
    path = Path(get_app_dir("scht_lab")) / "topo.json"
    if isinstance(topo, Topology):
        topo = to_model(topo)
    async with await open_file(path, "w") as f:
        await f.write(topo.model_dump_json())