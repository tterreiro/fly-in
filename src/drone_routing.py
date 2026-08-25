from src import Graph, Zone
from typing import Any
from heapq import heappop, heappush


class RoutingError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(msg)

    def __str__(self) -> str:
        return f"RoutingError: {self.msg}"


class DroneRouter:
    def __init__(self, nb_drones: int, graph: Graph) -> None:
        self.drones = nb_drones
        self.graph = graph
        # (zone_name, turn_number):nb_drones occupying
        self.zone_reserves: dict[tuple[str, int], int] = {}
        # (connection_id, turn_number):nb_drones occupying
        self.link_reserves: dict[tuple[str, int], int] = {}
        self.flees_path: dict[str, list] = {}  # {drone_id: [path_sequence]}

    def plan_routes(self) -> None:
        start_hub = self.graph.start_hub
        end_hub = self.graph.end_hub
        for drone_id in range(1, self.drones + 1):
            path = self.path_finder(start_hub,
                                    end_hub)
            if not path:
                raise RoutingError(f"Drone {drone_id} failed to fly.\n"
                                   "Fix your path!")
            self.flees_path[f"drone_{drone_id}"] = path
            self._reserve_path(path)
        print(self.flees_path)

    def path_finder(self, start: Zone, end: Zone) -> list[tuple[str, int]]:
        pq = []
        #  (turn, zone_name, list[zones drone has travelled (zone_name, turn)])
        heappush(pq, (0, start.name, [(start.name, 0)]))
        visited: set[tuple[str, int]] = set()
        max_limited_turns = 200
        while pq:
            current_turn, current_zone, history = heappop(pq)

            if current_zone == end.name:
                return history

            # limit the max turns possible to prevent infinite loops
            if current_turn > max_limited_turns:
                continue

            state = (current_zone, current_turn)
            if state in visited:
                continue
            visited.add(state)

            for connection in self.graph.connections.get(current_zone, []):
                # see which side of connection is neighbour
                neighbour_name = (connection.zone_b
                                  if connection.zone_a == current_zone
                                  else connection.zone_a)
                neighbour_zone = self.graph.zones[neighbour_name]

                # calculate arrival time
                if neighbour_zone.zone_type == "blocked":
                    continue
                if neighbour_zone.zone_type == "restricted":
                    arrival_time = current_turn + 2
                else:
                    arrival_time = current_turn + 1
                # organize alphabetically because of how the connects are made
                low = min(connection.zone_a, connection.zone_b)
                high = max(connection.zone_a, connection.zone_b)
                connection_key = f"{low}-{high}"
                # check connection capacity
                if (self.link_reserves.get((connection_key, current_turn), 0)
                        >= connection.max_capacity):
                    continue
                # check neighbour zone capacity
                if (self.zone_reserves.get((neighbour_name, arrival_time), 0)
                        >= neighbour_zone.max_drones):
                    continue
                # if it can move update heap
                new_history = list(history)
                new_history.append((neighbour_name, arrival_time))
                heappush(pq, (arrival_time, neighbour_name, new_history))

            # see if can wait one more turn
            next_turn = current_turn + 1
            current_zone_obj = self.graph.zones[current_zone]

            if (self.zone_reserves.get((current_zone, next_turn), 0)
                    < current_zone_obj.max_drones):
                wait_history = list(history)
                wait_history.append((current_zone, next_turn))
                heappush(pq, (next_turn, current_zone, wait_history))
        return []

    def _reserve_path(self, path: list[Any]) -> None:
        for name, turn in path:
            current_count = self.zone_reserves.get((name, turn), 0)
            self.zone_reserves[(name, turn)] = current_count + 1

        for i in range(len(path) - 1):
            current_step = path[i]
            next_step = path[i + 1]
            if current_step[0] != next_step[0]:
                # organize alphabetically
                low_zone = min(current_step[0], next_step[0])
                high_zone = max(current_step[0], next_step[0])
                connection = f"{low_zone}-{high_zone}"
                turn = current_step[1]
                current_count = self.link_reserves.get((connection, turn), 0)
                self.link_reserves[(connection, turn)] = current_count + 1
