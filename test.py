from src import MapParser

parser = MapParser()

nb_drones, graph = parser.parse("02_circular_loop.txt")
print(f"Drones: {nb_drones}\n Graph:\n {graph}")