from enum import Enum
from pydantic import BaseModel


class ZoneType(Enum):
    """Enumeration of possible zone types and their movement behaviors."""
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class Zone(BaseModel):
    """Representation of an individual hub or zone in the network.
    Attributes:
        name: Unique string name of the zone.
        x: X-coordinate for visual plotting.
        y: Y-coordinate for visual plotting.
        colour: Display color string.
        zone_type: Zone classification
                    ('normal', 'blocked', 'restricted', 'priority').
        max_drones: Maximum number of drones that may
                    occupy this zone simultaneously.
        hub_type: Special designation ('start_hub', 'end_hub', or 'default').
    """
    name: str
    x: int
    y: int
    colour: str
    zone_type: str
    max_drones: int
    # start_hub or end_hub
    hub_type: str


class Connection(BaseModel):
    """Bidirectional connection link between two zones.
    Attributes:
        zone_a: Identifier of the first connected zone.
        zone_b: Identifier of the second connected zone.
        max_capacity: Maximum simultaneous drones allowed traversing the link.
    """
    zone_a: str
    zone_b: str
    max_capacity: int


class Graph:
    """Graph network tracking zones, connections, and start/end hubs."""
    def __init__(self) -> None:
        """Initialize empty graph containers for zones and adjacency lists."""
        # zones = {zone_name: zone_object}
        self.zones: dict[str, Zone] = {}
        # adj_list = {zone_name: [list of connections objects linked to it]}
        self.connections: dict[str, list[Connection]] = {}
        # start and end zone
        self.start_hub: Zone
        self.end_hub: Zone

    def __str__(self) -> str:
        """
        Return a formatted string representing zones and connection lists.
        """
        return f"Zones: {self.zones}\n\nConnections: {self.connections}\n"

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph and record start and end hubs.
        Args:
            zone: Zone instance to register in the network.
        """
        self.zones[zone.name] = zone
        self.connections[zone.name] = []
        if zone.hub_type == 'start_hub':
            self.start_hub = zone
        if zone.hub_type == 'end_hub':
            self.end_hub = zone

    def add_connection(self, connection: Connection) -> None:
        """Register a bidirectional connection between two zones.
        Args:
            connection: Connection instance to add to both adjacent zones.
        """
        self.connections[connection.zone_a].append(connection)
        self.connections[connection.zone_b].append(connection)

    def get_neighbours(self, zone: str) -> list[str]:
        """Return names of accessible, non-blocked adjacent zones.
        Args:
            zone: Name of the zone whose neighbours should be returned.
        Returns:
            list[str]: Names of accessible neighbouring zones.
        """
        neighbours: list[str] = []
        for connection in self.connections.get(zone, []):
            neighbour_name = (connection.zone_b if connection.zone_a == zone
                              else connection.zone_a)
            if self.zones[neighbour_name].zone_type != ZoneType.BLOCKED.value:
                neighbours.append(neighbour_name)
        return neighbours
