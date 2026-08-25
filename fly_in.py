#!/usr/bin/env python3
import sys
from src import MapParser, DroneRouter, GraphViz


def flyin() -> None:
    """Main entry point for the map parsing, drone routing and displaying"""
    try:
        if len(sys.argv) == 1:
            GraphViz.render()
        elif len(sys.argv) == 2:
            parser = MapParser()
            nb_drones, graph = parser.parse(sys.argv[1])
            drone_router = DroneRouter(nb_drones, graph)
            drone_router.plan_routes()
        else:
            print("Usage: python3 fly_in.py [config.txt]")
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    flyin()
