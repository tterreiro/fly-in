from entities import Graph, Zone
from typing import Any
from heapq import heappop, heappush


class RoutingError(Exception):
    """
    Exception raised when pathfinding or turn scheduling cannot be solved.
    """
    def __init__(self, msg: str) -> None:
        """Initialize routing error with description.
        Args:
            msg: Failure reason or description.
        """
        self.msg = msg
        super().__init__(msg)

    def __str__(self) -> str:
        """Return formatted routing error string."""
        return f"RoutingError: {self.msg}"


class DroneRouter:
    """Time-expanded conflict-free router for scheduling drone fleets."""
    def __init__(self, nb_drones: int, graph: Graph) -> None:
        """Initialize the router with fleet size and network graph.
        Args:
            nb_drones: Number of drones to route from start to destination.
            graph: Graph instance representing the map network.
        """
        self.drones = nb_drones
        self.graph = graph
        # (zone_name, turn_number):nb_drones occupying
        self.zone_reserves: dict[tuple[str, int], int] = {}
        # (connection_id, turn_number):nb_drones occupying
        self.link_reserves: dict[tuple[str, int], int] = {}
        # {drone_id: [path_sequence]}
        self.flees_path: dict[str, list[tuple[str, int]]] = {}

    def plan_routes(self) -> None:
        """
        Plan sequential conflict-free routes
        for all drones and print simulation.
        Raises:
            RoutingError: If any drone fails
                          to find a valid route to the end hub.
        """
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
        self.print_simulation()

    def print_simulation(self) -> None:
        """Outputs turn by turn simulation moves"""
        if not self.flees_path:
            return

        turn_moves: dict[int, list[str]] = {}
        max_turns = 0

        for drone_id in range(1, self.drones + 1):
            path = self.flees_path.get(f"drone_{drone_id}", [])
            for i in range(len(path) - 1):
                prev_zone, prev_turn = path[i]
                curr_zone, curr_turn = path[i + 1]

                if prev_zone == curr_zone:
                    continue
                if curr_turn - prev_turn == 1:
                    turn_moves.setdefault(
                        curr_turn, []).append(f"D{drone_id}-{curr_zone}")
                elif curr_turn - prev_turn == 2:
                    turn_moves.setdefault(prev_turn + 1, []).append(
                        f"D{drone_id}-{prev_zone}-{curr_zone}"
                    )
                    turn_moves.setdefault(
                        curr_turn, []).append(f"D{drone_id}-{curr_zone}")

                if curr_turn > max_turns:
                    max_turns = curr_turn

        for turn in range(1, max_turns + 1):
            moves = turn_moves.get(turn, [])
            if moves:
                print(" ".join(moves))

    def path_finder(self, start: Zone, end: Zone) -> list[tuple[str, int]]:
        """Find the earliest arrival conflict-free path between two zones.
        Args:
            start: Origin Zone instance.
            end: Target destination Zone instance.
        Returns:
            list[tuple[str, int]]: Sequence of (zone_name, turn) states.
        """
        # (turn, -priority_count, zone_name, history)
        pq: list[tuple[int, int, str, list[tuple[str, int]]]] = []
        init_prio = 1 if start.zone_type == "priority" else 0
        heappush(pq, (0, -init_prio, start.name, [(start.name, 0)]))
        visited: set[tuple[str, int]] = set()
        max_limited_turns = 200

        while pq:
            current_turn, neg_prio, current_zone, history = heappop(pq)
            prio_count = -neg_prio

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
                if neighbour_zone.zone_type == "blocked":
                    continue

                # calculate arrival time and duration
                is_restricted = (neighbour_zone.zone_type == "restricted")
                duration = 2 if is_restricted else 1
                arrival_time = current_turn + duration

                # organize alphabetically because of how the connects are made
                low = min(connection.zone_a, connection.zone_b)
                high = max(connection.zone_a, connection.zone_b)
                connection_key = f"{low}-{high}"

                # check connection capacity
                ck = connection_key
                link_full = any(
                    self.link_reserves.get((ck, current_turn + dt), 0)
                    >= connection.max_capacity
                    for dt in range(duration)
                )
                if link_full:
                    continue

                # check neighbour zone capacity
                if neighbour_name != end.name:
                    if (self.zone_reserves.get(
                        (neighbour_name, arrival_time), 0)
                            >= neighbour_zone.max_drones):
                        continue

                # check next zone prio if it can move update heap
                is_prio = 1 if neighbour_zone.zone_type == "priority" else 0
                new_prio = prio_count + is_prio

                new_history = list(history)
                new_history.append((neighbour_name, arrival_time))
                heappush(
                    pq, (arrival_time, -new_prio, neighbour_name, new_history)
                    )

            # see if can wait one more turn
            next_turn = current_turn + 1
            current_zone_obj = self.graph.zones[current_zone]

            if (self.zone_reserves.get((current_zone, next_turn), 0)
                    < current_zone_obj.max_drones):
                wait_history = list(history)
                wait_history.append((current_zone, next_turn))
                heappush(
                    pq, (next_turn, -prio_count, current_zone, wait_history)
                    )
        return []

    def _reserve_path(self, path: list[Any]) -> None:
        """Reserve zone and link capacities along a planned drone route.
        Args:
            path: Chronological list of (zone_name, turn) tuples
                  for a single drone.
        """
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

                start_turn = current_step[1]
                duration = next_step[1] - current_step[1]
                for t in range(start_turn, start_turn + duration):
                    key = (connection, t)
                    count = self.link_reserves.get(key, 0)
                    self.link_reserves[key] = count + 1
