from mininet.topo import Topo
from collections import OrderedDict

from math import sqrt, log
import json
with open("cities.json", "r") as f:
    cities = OrderedDict(json.load(f, object_pairs_hook=OrderedDict))

def city_index(city):
    return list(cities.keys()).index(city)

class LabTopo( Topo ):
    "Simple topology example."

    def delay_calc(self, distance):
        return f"{distance/200}ms"

    def jitter_calc(self, distance):
        return f"{log(sqrt(distance/200))}ms"

    def bandwidth_calc(self, city, neighbor):
        return (cities[city]["population"] + cities[neighbor]["population"] + 10*max(cities[city]["population"], cities[neighbor]["population"])) / 9000000 - cities[city]["neighbors"][neighbor] / 3 + (cities[city]["connectivity"] + cities[neighbor]["connectivity"]) * 90

    def loss_calc(self, city, neighbor):
        return (cities[city]["population"] + cities[neighbor]["population"] + max(cities[city]["population"], cities[neighbor]["population"])) / 2000000000 + cities[city]["neighbors"][neighbor] / 1500000

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        for city in cities.keys():
            self.addHost(f"h{city}", ip=f"10.0.0.{city_index(city)+1}")
            self.addSwitch(f"s{city_index(city)+1}", dpid=hex(city_index(city)+1)[2:])
            self.addLink(f"h{city}", f"s{city_index(city)+1}", delay="1ms", bw=1000, loss=0.01)
        print("Initial link parameters:")
        # Link cities
        for city in cities.keys():
            for neighbor in cities[city]["neighbors"].keys():
                try:
                    if self.linkInfo(f"s{city_index(city)+1}", f"s{city_index(neighbor)+1}") is not None:
                        continue
                except:
                    pass
                delay = self.delay_calc(cities[city]["neighbors"][neighbor])
                jitter = self.jitter_calc(cities[city]["neighbors"][neighbor])
                bandwidth=self.bandwidth_calc(city, neighbor)
                loss=self.loss_calc(city, neighbor)
                self.addLink(
                    f"s{city_index(city)+1}",
                    f"s{city_index(neighbor)+1}",
                    delay=delay,
                    jitter=jitter,
                    bw=bandwidth,
                    loss=loss
                )
                print(f"{city} <-> {neighbor}: delay={delay}, jitter={jitter}, bandwidth={bandwidth}, loss={loss}")

topos = { 'labtopo': ( lambda: LabTopo() ) }