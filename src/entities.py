from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class Zone(BaseModel):
    name: str
    x: int
    y: int
    colour: str = Field(default='white')
    zone_type: ZoneType = Field(default=ZoneType.NORMAL)
    max_drones: int = Field(default=1)
    hub_type: str


class Connection(BaseModel):
    zone_a: str
    zone_b: str
    max_capacity: int = Field(default=1)


class Graph:
    def __init__(self) -> None:
        # zones = {zone_name: zone_object}
        self.zones: dict[str, Zone] = {}
        # adj_list = {zone_name: [list of connections objects linked to it]}
        self.connections_list: dict[str, list[Connection]] = {}
        # start and end zone
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.connections_list[zone.name] = []
        if zone.hub_type == 'start_hub':
            self.start_hub = zone
        if zone.hub_type == 'end_hub':
            self.end_hub = zone

    def add_connection(self, connection: Connection) -> None:
        self.connections_list[connection.zone_a].append(connection)
        self.connections_list[connection.zone_b].append(connection)

    def get_neighbours(self, zone: str) -> list[str]:
        neighbours: list[str] = []
        for connection in self.connections_list.get(zone, []):
            neighbour_name = (connection.zone_b if connection.zone_a == zone
                              else connection.zone_a)
            if self.zones[neighbour_name].zone_type != ZoneType.BLOCKED:
                neighbours.append(neighbour_name)
        return neighbours
