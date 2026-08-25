import os
import pygame
from src import DroneRouter, Graph, MapParser


class RenderingError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(msg)

    def __str__(self) -> str:
        return f"Failed to load/route:: {self.msg}"


class GraphViz:
    SKY_BACKGROUND_PATH = os.path.join("assets", "skybackground.jpg")
    DRONE_ASSET_PATH = os.path.join("assets", "airplane_kamikaze.png")

    @staticmethod
    def _find_map_files(maps_dir: str = "maps") -> list[str]:
        map_files = []
        if not os.path.exists(maps_dir):
            return map_files
        for root, _, files in os.walk(maps_dir):
            for file in sorted(files):
                if file.endswith(".txt"):
                    map_files.append(os.path.join(root, file))
        return map_files

    @staticmethod
    def _compute_screen_coords(
        graph: Graph,
        width: int,
        height: int,
        margin: int = 140
    ) -> dict[str, tuple[int, int]]:
        xs = [zone.x for zone in graph.zones.values()]
        ys = [zone.y for zone in graph.zones.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max_x - min_x
        span_y = max_y - min_y

        usable_w = width - 2 * margin
        usable_h = height - 2 * margin

        screen_pos = {}
        for name, zone in graph.zones.items():
            if span_x == 0:
                px = width // 2
            else:
                norm_x = (zone.x - min_x) / span_x
                px = int(margin + norm_x * usable_w)

            if span_y == 0:
                py = height // 2
            else:
                norm_y = (zone.y - min_y) / span_y
                py = int(height - margin - norm_y * usable_h)

            screen_pos[name] = (px, py)

        return screen_pos

    @staticmethod
    def _parse_colour(col_str: str) -> tuple[int, int, int]:
        color_map = {
            "green": (46, 204, 113),
            "red": (231, 76, 60),
            "blue": (52, 152, 219),
            "yellow": (241, 196, 15),
            "orange": (230, 126, 34),
            "purple": (155, 89, 182),
            "cyan": (26, 188, 156),
            "lime": (120, 224, 143),
            "gold": (246, 185, 59),
            "brown": (121, 85, 72),
            "black": (44, 62, 80),
            "white": (236, 240, 241),
            "maroon": (128, 0, 0),
            "darkred": (139, 0, 0),
            "violet": (186, 85, 211),
            "magenta": (255, 0, 255)
        }
        return color_map.get(col_str.lower(), (200, 200, 200))

    @staticmethod
    def _get_drone_state_at_turn(
        path: list[tuple[str, int]],
        turn: int
    ) -> tuple[str, str, int]:
        """Returns (current_hub, next_hub, arrival_turn)."""
        if not path:
            return ("", "", 0)
        if turn <= path[0][1]:
            nxt = path[1][0] if len(path) > 1 else path[0][0]
            nxt_t = path[1][1] if len(path) > 1 else path[0][1]
            return (path[0][0], nxt, nxt_t)
        if turn >= path[-1][1]:
            return (path[-1][0], "ARRIVED", path[-1][1])

        curr_loc = path[0][0]
        curr_idx = 0
        for idx, (name, t) in enumerate(path):
            if t <= turn:
                curr_loc = name
                curr_idx = idx
            else:
                break

        if curr_idx + 1 < len(path):
            nxt_loc = path[curr_idx + 1][0]
            nxt_turn = path[curr_idx + 1][1]
        else:
            nxt_loc = curr_loc
            nxt_turn = turn
        return (curr_loc, nxt_loc, nxt_turn)

    @classmethod
    def render(cls) -> None:
        pygame.init()
        screen_w, screen_h = 1600, 1000
        screen = pygame.display.set_mode((screen_w, screen_h))
        pygame.display.set_caption("Fly-In: Drone Routing Simulator")
        clock = pygame.time.Clock()

        font_title = pygame.font.SysFont("Arial", 28, bold=True)
        font_main = pygame.font.SysFont("Arial", 18)
        font_small = pygame.font.SysFont("Arial", 13, bold=True)
        font_debug = pygame.font.SysFont("Consolas", 12)

        bg_img = None
        if os.path.exists(cls.SKY_BACKGROUND_PATH):
            bg_img = pygame.image.load(cls.SKY_BACKGROUND_PATH).convert()
            bg_img = pygame.transform.scale(bg_img, (screen_w, screen_h))

        drone_sprite = None
        if os.path.exists(cls.DRONE_ASSET_PATH):
            raw_drone = pygame.image.load(cls.DRONE_ASSET_PATH).convert_alpha()
            drone_w = 36
            ratio = drone_w / raw_drone.get_width()
            drone_h = int(raw_drone.get_height() * ratio)
            drone_size = (drone_w, drone_h)
            drone_sprite = pygame.transform.scale(raw_drone, drone_size)

        state = "MENU"
        map_files = cls._find_map_files("maps")
        selected_index = 0
        debug_mode = False

        graph = None
        drones_paths = {}
        max_turns = 0
        current_turn = 0
        node_pos = {}
        error_msg = ""

        running = True
        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if state == "SIMULATION":
                            state = "MENU"
                            error_msg = ""
                        else:
                            running = False

                    elif state == "MENU":
                        if event.key == pygame.K_UP:
                            count = max(1, len(map_files))
                            selected_index = (selected_index - 1) % count
                        elif event.key == pygame.K_DOWN:
                            count = max(1, len(map_files))
                            selected_index = (selected_index + 1) % count
                        elif event.key == pygame.K_RETURN and map_files:
                            try:
                                sel = map_files[selected_index]
                                nb, p_graph = MapParser.parse(sel)
                                router = DroneRouter(nb, p_graph)
                                router.plan_routes()

                                graph = p_graph
                                drones_paths = router.flees_path
                                if drones_paths:
                                    max_turns = max(
                                        p[-1][1] for p in drones_paths.values()
                                    )
                                else:
                                    max_turns = 0
                                current_turn = 0
                                node_pos = cls._compute_screen_coords(
                                    graph, screen_w, screen_h
                                )
                                state = "SIMULATION"
                                error_msg = ""
                            except Exception as e:
                                raise RenderingError(f"{e}")

                    elif state == "SIMULATION":
                        if event.key in (pygame.K_RIGHT, pygame.K_UP):
                            if current_turn < max_turns:
                                current_turn += 1
                        elif event.key in (pygame.K_LEFT, pygame.K_DOWN):
                            if current_turn > 0:
                                current_turn -= 1
                        elif event.key == pygame.K_d:
                            debug_mode = not debug_mode

            if bg_img:
                screen.blit(bg_img, (0, 0))
            else:
                screen.fill((30, 40, 50))

            if state == "MENU":
                title_surf = font_title.render(
                    "SELECT A MAP", True, (255, 255, 255)
                )
                screen.blit(
                    title_surf,
                    (screen_w // 2 - title_surf.get_width() // 2, 40)
                )

                start_y = 120
                for i, map_path in enumerate(map_files):
                    is_selected = (i == selected_index)
                    color = (255, 215, 0) if is_selected else (220, 220, 220)
                    prefix = "->  " if is_selected else "    "
                    item_surf = font_main.render(
                        f"{prefix}{map_path}", True, color
                    )
                    screen.blit(item_surf, (80, start_y + i * 30))

                hint_str = "UP/DOWN: Navigate | ENTER: Select | ESC: Exit"
                hint_surf = font_small.render(hint_str, True, (160, 180, 200))
                screen.blit(
                    hint_surf,
                    (screen_w // 2 - hint_surf.get_width() // 2, screen_h - 40)
                )

                if error_msg:
                    err_surf = font_main.render(
                        error_msg, True, (255, 80, 80)
                    )
                    screen.blit(
                        err_surf,
                        (screen_w // 2 - err_surf.get_width() // 2,
                         screen_h - 80)
                    )

            elif state == "SIMULATION" and graph:
                hub_occupancy: dict[str, list[str]] = {
                    name: [] for name in graph.zones
                }
                drone_info: dict[str, tuple[str, str, int]] = {}
                link_usage: dict[tuple[str, str], int] = {}

                for drone_id, path in drones_paths.items():
                    curr_loc, nxt_loc, arr_t = cls._get_drone_state_at_turn(
                        path, current_turn
                    )
                    drone_info[drone_id] = (curr_loc, nxt_loc, arr_t)
                    if curr_loc in hub_occupancy:
                        hub_occupancy[curr_loc].append(drone_id)

                    if curr_loc != nxt_loc and nxt_loc != "ARRIVED":
                        link_key = tuple(sorted([curr_loc, nxt_loc]))
                        link_usage[link_key] = (
                            link_usage.get(link_key, 0) + 1
                        )

                drawn_links = set()
                for zone_name, conns in graph.connections.items():
                    for conn in conns:
                        pair = tuple(sorted([conn.zone_a, conn.zone_b]))
                        if pair not in drawn_links:
                            drawn_links.add(pair)
                            p1 = node_pos[conn.zone_a]
                            p2 = node_pos[conn.zone_b]
                            active = link_usage.get(pair, 0)

                            if debug_mode and active >= conn.max_capacity:
                                line_color = (230, 40, 40)
                                line_width = 5
                            else:
                                line_color = (60, 80, 100)
                                line_width = 3

                            pygame.draw.line(
                                screen, line_color, p1, p2, line_width
                            )

                            if debug_mode:
                                mid_x = (p1[0] + p2[0]) // 2
                                mid_y = (p1[1] + p2[1]) // 2
                                cap_str = f"{active}/{conn.max_capacity}"
                                cap_lbl = font_debug.render(
                                    cap_str, True, (20, 30, 40)
                                )
                                screen.blit(
                                    cap_lbl,
                                    (mid_x - cap_lbl.get_width() // 2,
                                     mid_y - 12)
                                )

                for name, zone in graph.zones.items():
                    pos = node_pos[name]
                    radius = 24
                    base_color = cls._parse_colour(zone.colour)
                    occ_count = len(hub_occupancy[name])

                    if zone.hub_type == "start_hub":
                        pygame.draw.circle(
                            screen, (0, 255, 128), pos, radius + 5, 3
                        )
                    elif zone.hub_type == "end_hub":
                        pygame.draw.circle(
                            screen, (255, 50, 50), pos, radius + 5, 3
                        )

                    is_special = zone.hub_type in ("start_hub", "end_hub")
                    if (debug_mode and occ_count >= zone.max_drones
                            and not is_special):
                        pygame.draw.circle(
                            screen, (255, 0, 0), pos, radius + 8, 2
                        )

                    pygame.draw.circle(screen, base_color, pos, radius)
                    pygame.draw.circle(screen, (20, 20, 20), pos, radius, 2)

                    name_surf = font_small.render(name, True, (0, 0, 0))
                    screen.blit(
                        name_surf,
                        (pos[0] - name_surf.get_width() // 2,
                         pos[1] - radius - 18)
                    )

                    cap_surf = font_small.render(
                        f"{occ_count}/{zone.max_drones}", True, (20, 20, 20)
                    )
                    screen.blit(
                        cap_surf,
                        (pos[0] - cap_surf.get_width() // 2,
                         pos[1] - cap_surf.get_height() // 2)
                    )

                for hub_name, drones in hub_occupancy.items():
                    if not drones:
                        continue
                    hx, hy = node_pos[hub_name]
                    count = len(drones)
                    for idx, d_id in enumerate(drones):
                        offset_x = (idx - (count - 1) / 2) * 42
                        dx = int(hx + offset_x)
                        dy = hy + 30

                        if drone_sprite:
                            screen.blit(
                                drone_sprite,
                                (dx - drone_sprite.get_width() // 2, dy)
                            )
                        else:
                            pygame.draw.circle(
                                screen, (255, 230, 0), (dx, dy), 6
                            )

                        short_id = d_id.replace("drone_", "D")
                        d_lbl = font_debug.render(short_id, True, (0, 0, 0))
                        screen.blit(
                            d_lbl,
                            (dx - d_lbl.get_width() // 2, dy + 22)
                        )

                turn_txt = f"Turn: {current_turn} / {max_turns}"
                turn_surf = font_title.render(turn_txt, True, (0, 0, 0))
                screen.blit(turn_surf, (30, 20))

                help_s = "ARROWS: Step Turn | D: Debug Overlay | ESC: Menu"
                help_surf = font_small.render(help_s, True, (30, 40, 50))
                screen.blit(help_surf, (30, screen_h - 35))

                if debug_mode:
                    panel_w = 280
                    max_h = screen_h - 100
                    panel_h = min(max_h, 30 + len(drones_paths) * 22)

                    panel_x = screen_w - panel_w - 20
                    panel_y = 20

                    top_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
                    pad = 45
                    has_overlap = any(
                        top_rect.inflate(pad, pad).collidepoint(pos)
                        for pos in node_pos.values()
                    )

                    if has_overlap:
                        panel_y = screen_h - panel_h - 45

                    panel_surf = pygame.Surface(
                        (panel_w, panel_h), pygame.SRCALPHA
                    )
                    panel_surf.fill((20, 30, 40, 225))
                    screen.blit(panel_surf, (panel_x, panel_y))

                    hdr = font_debug.render(
                        "DRONE ROUTING DEBUG [D]", True, (255, 215, 0)
                    )
                    screen.blit(hdr, (panel_x + 10, panel_y + 10))

                    for idx, (d_id, info) in enumerate(drone_info.items()):
                        curr, nxt, arr_t = info
                        y_pos = panel_y + 35 + idx * 22
                        if nxt == "ARRIVED":
                            line = f"{d_id}: AT {curr} (DONE)"
                            col = (100, 255, 100)
                        elif curr == nxt:
                            line = f"{d_id}: WAIT @ {curr}"
                            col = (255, 200, 100)
                        else:
                            line = f"{d_id}: {curr} -> {nxt} (T:{arr_t})"
                            col = (200, 230, 255)
                        screen.blit(
                            font_debug.render(line, True, col),
                            (panel_x + 10, y_pos)
                        )

            pygame.display.flip()

        pygame.quit()
