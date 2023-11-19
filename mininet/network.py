from mininet.topo import Topo
from collections import OrderedDict

from math import sqrt, log
import json


class LabTopo( Topo ):
    "Simple topology example."
    def city_index(self, city):
        return list(self.cities.keys()).index(city)

    def delay_calc(self, distance):
        return f"{distance/200}ms"

    def jitter_calc(self, distance):
        return f"{log(sqrt(distance/200))}ms"

    def bandwidth_calc(self, city, neighbor):
        if self.cities[city].get("bw_overrides", False):
            if self.cities[city]["bw_overrides"].get(neighbor, False):
                return self.cities[city]["bw_overrides"][neighbor]
        return max((self.cities[city]["population"] + self.cities[neighbor]["population"] + 10*max(self.cities[city]["population"], self.cities[neighbor]["population"])) / 9000000 - self.cities[city]["neighbors"][neighbor] / 3 + (self.cities[city]["connectivity"] + self.cities[neighbor]["connectivity"]) * 90,
                   min(self.cities[city]["population"], self.cities[neighbor]["population"])/(self.cities[city]["population"] + self.cities[neighbor]["population"]) * 100 + self.cities[city]["neighbors"][neighbor]/12 - (75/(min(self.cities[city]["connectivity"], self.cities[neighbor]["connectivity"]))))

    def loss_calc(self, city, neighbor):
        return (self.cities[city]["population"] + self.cities[neighbor]["population"] + max(self.cities[city]["population"], self.cities[neighbor]["population"])) / 2000000000 + self.cities[city]["neighbors"][neighbor] / 1500000

    def build( self, filename="self.cities.json" ):
        "Create custom topo."
        with open(filename, "r") as f:
            self.cities = OrderedDict(json.load(f, object_pairs_hook=OrderedDict))
        # Add hosts and switches
        for city in self.cities.keys():
            self.addHost(f"h{city}", ip=f"10.0.0.{self.city_index(city)+1}")
            self.addSwitch(f"s{self.city_index(city)+1}", dpid=hex(self.city_index(city)+1)[2:])
            self.addLink(f"h{city}", f"s{self.city_index(city)+1}", delay="1ms", bw=1000, loss=0.01)
        print("Initial link parameters:")
        # Link cities
        for city in self.cities.keys():
            for neighbor in self.cities[city]["neighbors"].keys():
                try:
                    if self.linkInfo(f"s{self.city_index(city)+1}", f"s{self.city_index(neighbor)+1}") is not None:
                        continue
                except:
                    pass
                delay = self.delay_calc(self.cities[city]["neighbors"][neighbor])
                jitter = self.jitter_calc(self.cities[city]["neighbors"][neighbor])
                bandwidth=self.bandwidth_calc(city, neighbor)
                loss=self.loss_calc(city, neighbor)
                self.addLink(
                    f"s{self.city_index(city)+1}",
                    f"s{self.city_index(neighbor)+1}",
                    delay=delay,
                    jitter=jitter,
                    bw=bandwidth,
                    loss=loss
                )
                print(f"{city} <-> {neighbor}: delay={delay}, jitter={jitter}, bandwidth={bandwidth}, loss={loss}")

def get_topo(filename="topo.json"):
    return LabTopo(filename=filename)

topos = { 'labtopo': get_topo }