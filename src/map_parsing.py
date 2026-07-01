

# ---- FINISH METADATA CHECKING ---

from src import Graph, ZoneType


class ParsingError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(msg)

    def __str__(self) -> str:
        return f"ParsingError: {self.msg}"


class MapParser:
    @staticmethod
    def parse_metadata(meta_string: str) -> dict[str, str]:
        metadata = {}
        tokens = meta_string.replace('[', '').replace(']', '').split()
        for token in tokens:
            if '=' in token:
                key, value = token.split('=', 1)
                key = key.lower()
                if key == 'zone' and value.lower() not in ZoneType:
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
                metadata[key.strip()] = value.lower().strip()
        return metadata

    @staticmethod
    def parse(input_file: str) -> tuple[int, Graph]:  # (nb_drones, graph)
        """Parse configuration file and validate map settings."""
        graph = Graph()
        raw_zones: list[str] = []
        raw_connections: list[str] = []
        zones_names = []
        is_first_line = True
        nb_start_hub = 0
        nb_end_hub = 0
        with open(input_file, "r") as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.split('#')[0].strip().lower()
                if not clean_line:
                    continue

                key, value = line.split(':', 1)
                key = key.strip().lower()

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
                        print(f"nb_drones has to be a number, dummy! ({e})")
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
            if '[' in zone:
                metadata = MapParser.parse_metadata(zone.split('[', 1)[1])
                zone = zone.split('[', 1)[0].strip()
            if zone.startswith("start_hub"):
                data: list[str] = zone.split(' ')
                if len(data) > 4:
                    raise ParsingError("Hub creation must follow the rules: "
                                       "start_hub: <name> <x> <y>")
                name = data[1]
                (x, y) = (data[2], data[3])
                if ' ' in name or '-' in name:
                    raise ParsingError("Zone names mustn't contain spaces or "
                                       "dashes!")
                if name in zones_names:
                    raise ParsingError("Every the zone name must be unique!")
                if not int(x) or not int(y):
                    raise ParsingError("Zones coordinates must be numbers!"
                                       f" ({x}, {y})")
                zones_names.append(name)
                nb_start_hub += 1
