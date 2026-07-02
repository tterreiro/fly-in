

# ---- FINISH METADATA CHECKING ---

from src import Graph, ZoneType, Zone, Connection


class ParsingError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(msg)

    def __str__(self) -> str:
        return f"ParsingError: {self.msg}"


class MapParser:
    @staticmethod
    def parse_metadata(meta_string: str,
                       metadata: dict[str, str]) -> dict[str, str]:
        tokens = meta_string.replace('[', '').replace(']', '').split()
        for token in tokens:
            if '=' in token:
                key, value = token.split('=', 1)
                key = key.lower().strip()
                valid_zones = [item.value for item in ZoneType]
                if key == 'zone' and value.lower() not in valid_zones:
                    raise ParsingError("Invalid zone type. Must be Normal, "
                                       "Blocked, Restricted or Priority")
                elif key == 'color' and not value.isalpha():
                    raise ParsingError("Invalid colour value! "
                                       "Must be a single-word string")
                elif key == 'max_drones' and int(value) <= 0:
                    raise ParsingError("Invalid ammount of drones."
                                       "Must be more than 0.")
                elif key == 'max_link_capacity' and int(value) <= 0:
                    raise ParsingError("Invalid ammount of max link capacity"
                                       "drones. Must be more than 0.")
                metadata[key] = value.lower().strip()
        return metadata

    @staticmethod
    def parse(input_file: str) -> tuple[int, Graph]:  # (nb_drones, graph)
        """Parse configuration file and validate map settings."""
        graph = Graph()
        raw_zones: list[str] = []
        raw_connections: list[str] = []
        zone_names = []
        is_first_line = True
        nb_start_hub = 0
        nb_end_hub = 0
        nb_drones = 1
        with open(input_file, "r") as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.split('#')[0].strip().lower()
                if not clean_line:
                    continue
                if is_first_line:
                    try:
                        if clean_line.startswith("nb_drones"):
                            nb_drones = clean_line.split(':', 1)[1].strip()
                            nb_drones = int(nb_drones)
                            if nb_drones < 1:
                                raise ParsingError(
                                    "Number of drones must be more than 0")
                            is_first_line = False
                            continue
                        else:
                            raise ParsingError("First line must be nb_drones.")
                    except Exception as e:
                        raise ParsingError(
                            f"nb_drones has to be a number, dummy! ({e})")
                if (clean_line.startswith("hub")
                    or clean_line.startswith("start_hub")
                        or clean_line.startswith("end_hub")):
                    raw_zones.append(clean_line)
                elif clean_line.startswith("connection"):
                    raw_connections.append(clean_line)
                else:
                    raise ParsingError(
                        "Unrecognized syntax error on line"
                        f"{line_num} ({clean_line})")

        for zone in raw_zones:
            metadata = {'zone': 'normal',
                    'color': 'white',
                    'max_drones': '1',
                    'max_link_capacity': '1'}
            if '[' in zone:
                metadata = MapParser.parse_metadata(zone.split('[', 1)[1],
                                                    metadata)
                zone = zone.split('[', 1)[0].strip()
            if "hub" in zone:
                data: list[str] = zone.split()
                if len(data) > 4:
                    raise ParsingError("Hub creation must follow the rules: "
                                       "hub: <name> <x> <y>")
                name = data[1]
                (x, y) = (data[2], data[3])
                hub_type = ("start_hub" if zone.startswith("starthub") 
                            else "end_hub" if zone.startswith("end_hub")
                            else "default")
                if ' ' in name or '-' in name:
                    raise ParsingError(
                        "Zone names mustn't contain spaces or dashes!")
                if name in zone_names:
                    raise ParsingError("Every the zone name must be unique!")
                try:
                    x = int(x)
                    y = int(y)
                except Exception:
                    raise ParsingError("Zones coordinates must be numbers!"
                                       f" ({x}, {y})")
                zone_names.append(name)
                if zone.startswith("start_hub"):
                    nb_start_hub += 1
                elif zone.startswith("end_hub"):
                    nb_end_hub += 1
                graph.add_zone(Zone(
                        name=name,
                        x=x,
                        y=y,
                        hub_type=hub_type,
                        colour=metadata["color"],
                        zone_type=metadata['zone'],
                        max_drones=int(metadata['max_drones'])))
        if nb_start_hub != 1 or nb_end_hub != 1:
            raise ParsingError("There must be exactly "
                               "one start and one end hub")
        for connection in raw_connections:
            metadata = {"max_link_capacity": '1'}
            if '[' in connection:
                metadata = MapParser.parse_metadata(
                    connection.split('[', 1)[1],
                    metadata)
                connection = connection.split('[', 1)[0].strip()
            # connected zones = [zone_a, zone_b]
            connected_zones: list[str] = connection.split()[1].split('-')
            zone_a = connected_zones[0]
            zone_b = connected_zones[1]
            if zone_a not in zone_names or zone_b not in zone_names:
                raise ParsingError("Connections must happen "
                                   f"between existing zones ({zone_names})")
            graph.add_connection(Connection(
                zone_a=zone_a,
                zone_b=zone_b,
                max_capacity=int(metadata['max_link_capacity'])))
        return (nb_drones, graph)

