from pydantic import BaseModel, RootModel


class Location(BaseModel):
    population: int
    connectivity: int
    neighbors: dict[str, int]

class Topology(RootModel):
    root: dict[str, Location]

    def __iter__(self):
        return iter(self.root)
    
    def __getitem__(self, key):
        return self.root[key]