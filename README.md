*This project has been created as part of the 42 curriculum by hde-andr.*


## Description

**Fly-in** is an algorithmic simulation project designed to manage and optimize the routing of multiple autonomous drones through a network of connected zones from a central start hub to a destination goal. The primary objective is to move all drones through the network in the fewest possible simulation turns while strictly respecting complex constraints, such as individual zone capacity limits (`max_drones`), connection traversal limits (`max_link_capacity`), and variable movement costs based on zone types (normal, priority, and 2-turn restricted zones). The project requires a complete object-oriented architecture built from scratch in Python without relying on external graph libraries.


## Instructions

The project includes a Makefile to automate setup, execution, linting, and cleanup tasks.
* **Installation:** Run `make install` to set up dependencies using your preferred package manager.
* **Execution:** Run `make run` to launch the simulator script.
* **Debugging:** Run `make debug` to execute the application with debugging tools.
* **Linting:** Run `make lint` to verify code quality using `flake8` and `mypy`.
* **Cleanup:** Run `make clean` to remove temporary caches and build artifacts.


## Algorithm Choices and Implementation Strategy

The architecture is structured around modular components handling map parsing, graph representation, path planning, and simulation execution.

* **Parsing & Graph Modeling:** The parser reads map configuration files line by line, validating zone types (normal, priority, restricted, blocked), metadata limits, and bidirectional connections while safely raising descriptive exceptions for malformed inputs. The network is represented as an object-oriented graph containing `Zone` and `Connection` instances.
* **Pathfinding & Turn Scheduling:** Path planning utilizes a customized priority-based pathfinding strategy inspired by Dijkstra's algorithm, adapted to evaluate movement costs (such as 2-turn penalties for restricted zones). The simulation engine schedules turns sequentially, ensuring that drones freeing up a zone release their capacity in the same turn. Multi-turn movements across restricted links manage edge occupancy dynamically without allowing drones to idle mid-connection.


## Visual Representation Features

The project implements a rich graphical user interface built with Pygame alongside terminal output capabilities:
* **Interactive Map Explorer:** A menu system allows users to browse and select map configuration text files directly within the window.
* **Smooth Animation & Rotation:** Drones smoothly interpolate their positions across simulation turns, and sprite rotations match their directional movement vectors along network edges.
* **Dynamic Debug Overlay:** Toggling debug mode (`D`) surfaces real-time zone types, active connection capacities, saturation warnings, and a status panel tracking individual drone states. These visual layers provide immediate clarity on bottleneck conditions and throughput efficiency.


## Resources

### References
To help me in the making of this project the following sources were used:
 * Peers
 * Pygame documentation
 * Youtube vidos about algorithms

### AI Usage Declaration
 * Helping in the understanding of the subject and guide for the project.
 * Spotting mistakes and debugging
 * Making of this readme