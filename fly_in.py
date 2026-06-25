import sys
from src import MapParser, DroneRouter


def flyin() -> None:
    """Main entry point for the map parsing, drone routing and displaying"""
    if len(sys.argv) != 2:
        print("Usage: python3 fly_in.py config.txt")
        return

    try:
        parser = MapParser

        nb_drones, graph = parser.parse(sys.argv[1])

        drone_router = DroneRouter

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    flyin()