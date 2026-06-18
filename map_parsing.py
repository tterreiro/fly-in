

class MapNode:
    def __init__(self,
                 x: int,
                 y: int,
                 name: str,
                 colour: str = 'gray',
                 zone_type: str = 'normal') -> None:
        self.x = x
        self.y = y
        self.name = name
        self.colour = colour
        self.zone_type = zone_type
        self.previous: dict[str, int] = {}  # {node: max_link}
        self.next: dict[str, int] = {}  # {node: max_link}


class MapParser:
    pass
