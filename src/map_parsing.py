

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
                if key == 'zone' and value not in ZoneType:
                    raise ParsingError("Invalid zone type. Must be Normal, "
                                       "Blocked, Restricted or Priority")
                elif key == 'color' and value not in ZoneType:
                    raise ParsingError("Invalid zone type. Must be Normal, "
                                       "Blocked, Restricted or Priority")
                metadata[key.strip()] = value.strip()
        return metadata

    @staticmethod
    def parse(input_file: str) -> tuple[int, Graph]:  # (nb_drones, graph)
        """Parse configuration file and validate map settings."""
        graph = Graph()
        raw_zones: list[str] = []
        raw_connections: list[str] = []
        is_first_line = True
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
                zone = zone.split('[', 1)[1]
            if zone.startswith("start_hub"):
                pass
