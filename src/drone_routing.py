from src import Graph, Zone, Connection, ZoneType
from typing import Any
from heapq import heappop, heappush


class DroneRouter:
    def __init__(self, nb_drones: int, graph: Graph) -> None:
        self.drones = nb_drones
        self.graph = graph
        # (zone_name, turn_number) : nb_drones occupying
        self.zone_reserves: dict[tuple[str, int], int] = {}
        # (connection_id, turn_number) : nb_drones occupying
        self.link_reserves: dict[tuple[str, int], int] = {}
        self.flees_path: dict[int, list] = {}  # {drone_id: [path_sequence]}

    def plan_routes(self) -> None:
        start_hub = self.graph.start_hub
        end_hub = self.graph.end_hub
        for drone_id in range(1, self.drones + 1):
            path = self.path_finder(start_hub,
                                    end_hub)

            self.flees_path[drone_id] = path

            self._reserve_path(path)

    def path_finder(self, start: Zone, end: Zone) -> list[tuple[str, int]]:
        pq = []
        #  (turn, zone_name, list[zones drone has travelled (zone_name, turn)])
        heappush(pq, (0, start.name, [(start.name, 0)]))
        visited: set = set()
        while pq:
            current_turn, current_zone, history = pq

            if current_zone == end.name:
                return history

            if (current_zone, current_turn) in visited:
                continue
            visited.add((current_zone, current_turn))
            viable_neighbours: tuple[int, str]
            for neighbour in self.graph.get_neighbours(current_zone):
                neighbour_zone = self.graph.zones[neighbour]
                arrival_time = current_turn
                if neighbour_zone.zone_type == ZoneType.RESTRICTED:
                    arrival_time += 2
                else:
                    arrival_time += 1
            # CONTINUE FROM HERE
            # Check the Zone Capacity:
            # # The drone looks at the global reservation table for that neighbor zone at that exact arrival turn.
            # # It looks up how many drones are already booked there.
            # # If the number of bookings has already reached or exceeded that zone's maximum drone capacity, the zone is full.
            # # The drone drops this option immediately.

    def _reserve_path(self, path: list[Any]) -> None:
        for name, turn in path:
            current_count = self.zone_reserves.get((name, turn), 0)
            self.zone_reserves[(name, turn)] = current_count + 1

        for i in range(len(path) - 1):
            current_step = path[i]
            next_step = path[i + 1]
            if current_step[0] != next_step[0]:
                low_zone = min(current_step[0], next_step[0])
                high_zone = max(current_step[0], next_step[0])
                connection = f"{low_zone}-{high_zone}"
                turn = current_step[1]
                current_count = self.link_reserves.get((connection, turn), 0)
                self.link_reserves[(connection, turn)] = current_count + 1
