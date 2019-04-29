import copy
import random
import types
from typing import List

import math
import networkx as nx
from extended_networkx_tools import Creator, Analytics, Visual, Solver


class Annealing2:

    MOVE_TYPE_ADD = 0
    MOVE_TYPE_REMOVE = 1
    MOVE_TYPE_MOVE = 2

    graph: nx.Graph
    """
    The current graph that is under work.
    """
    adjacency_matrix: List[List[float]]
    """
    Matrix of all neighbours of the graph.
    """
    row_length: int
    """
    The row length of the graph.
    """

    temperature: float
    """
    The current temperature of the graph through the iterations.
    """
    iterations: int
    """
    How many iterations that should be done for every temperature step.
    """
    energy: float
    """
    The current energy of the graph through the iterations.
    """

    _optimization_function = None
    """
    Function that defines the energy measurement
    """

    def __init__(self, nxg: nx.Graph, start_temperature=10000, iterations=200):
        # Set the provided graph
        self.graph = nxg

        # Initialisation of the graph data
        self.temperature = start_temperature
        self.iterations = iterations
        self.adjacency_matrix = Analytics.get_neighbour_matrix(nxg)
        self.row_length = len(self.adjacency_matrix)

        # Default energy function
        self._optimization_function = self.fn_energy_combined

    @staticmethod
    def fn_energy_convergence_rate(nxg: nx.Graph):
        return Analytics.convergence_rate(nxg)

    @staticmethod
    def fn_energy_edge_cost(nxg: nx.Graph):
        return Analytics.total_edge_cost(nxg)

    @staticmethod
    def fn_energy_combined(nxg: nx.Graph):
        convergence_rate = Analytics.convergence_rate(nxg).real
        edge_cost = Analytics.total_edge_cost(nxg)
        return edge_cost / -math.log(convergence_rate)

    @staticmethod
    def get_optimization_function(parameter):
        if parameter == 'edge_cost':
            return Annealing2.fn_energy_edge_cost
        elif parameter == 'convergence_rate':
            return Annealing2.fn_energy_convergence_rate
        elif parameter == 'combined':
            return Annealing2.fn_energy_combined

    def set_optimization_parameter(self, parameter):
        self._optimization_function = self.get_optimization_function(parameter)

    def get_energy(self):
        return self._optimization_function(self.graph)

    def update_temperature(self):
        self.temperature = self.temperature * 0.92

    def solve(self, visualise=False):
        # If the graph is not connected, just make a path of it, as we must have a
        # connected graph initially.
        if not nx.is_connected(self.graph):
            self.graph = Solver.path(self.graph)

        best_graph = copy.deepcopy(self.graph)
        best_energy = math.inf

        # Get the initial energy
        self.energy = self.get_energy()

        while 0.001 < self.temperature:
            for i in range(0, self.iterations):
                origin = random.randint(0, self.row_length - 1)
                dest = random.randint(0, self.row_length - 1)
                new_dest = random.randint(0, self.row_length - 1)

                move_type = self.adjacency_matrix[origin][dest]
                if move_type == self.MOVE_TYPE_REMOVE:
                    if self.adjacency_matrix[origin][new_dest] == 0 and random.randint(0, 1) == 1:
                        move_type = self.MOVE_TYPE_MOVE

                if self.can_make_move(move_type, origin, dest, new_dest):
                    # Make the move
                    self.make_move(move_type, origin, dest, new_dest)
                    # Check if the graph is still valid or not
                    if not self.graph_is_valid(move_type, origin, dest, new_dest):
                        # If not, revert the move
                        self.revert_move(move_type, origin, dest, new_dest)
                    # Check if the new state is good
                    elif not self.evaluate_state():
                        # If not, also revert the graph
                        self.revert_move(move_type, origin, dest, new_dest)
                    else:
                        # Store the current energy
                        self.energy = self.get_energy()
                        # Make sure we keep the best state of the graph
                        if self.energy < best_energy:
                            best_graph = copy.deepcopy(self.graph)
                            best_adjacency_matrix = copy.deepcopy(self.adjacency_matrix)
                            best_energy = self.energy

            # Revert to keep the best graph
            self.graph = copy.deepcopy(best_graph)
            self.adjacency_matrix = copy.deepcopy(best_adjacency_matrix)
            # Set the current energy
            self.energy = self.get_energy()
            # Update the temperature after the new graph
            self.update_temperature()
            if visualise:
                self.print_state()
        return self.graph

    def evaluate_state(self):
        # Fetch the new energy cost for the graph
        new_energy = self.get_energy()

        # If the new energy is an improvement, the move is always saved.
        if new_energy < self.energy:
            return True

        # Otherwise calculate the energy level, if the temperature is high the system is
        # more inclined to keeping all changes. When the temperature "cools" the algorithm
        # becomes less and less inclined to keep changes that result in a regression in energy cost.
        e = math.exp(-(new_energy - self.energy) / self.temperature)

        # Pick a random float number between 0 and 1, if the variable e is larger than the random
        # number, we keep the change otherwise we revert it.
        if random.uniform(0, 1) < e:
            return True

        return False

    def make_move(self, move_type, origin, dest, new_dest=None):
        # We're trying to add an edge
        if move_type == self.MOVE_TYPE_ADD:
            Creator.add_weighted_edge(self.graph, origin, dest)
            self.adjacency_matrix[origin][dest] = 1
            self.adjacency_matrix[dest][origin] = 1
        # We're trying to remove an edge
        elif move_type == self.MOVE_TYPE_REMOVE:
            self.graph.remove_edge(origin, dest)
            self.adjacency_matrix[origin][dest] = 0
            self.adjacency_matrix[dest][origin] = 0
        # We're trying to move an edge
        elif move_type == self.MOVE_TYPE_MOVE:
            self.make_move(self.MOVE_TYPE_REMOVE, origin, dest)
            self.make_move(self.MOVE_TYPE_ADD, origin, new_dest)

    def revert_move(self, move_type, origin, dest, new_dest=None):
        if move_type == self.MOVE_TYPE_REMOVE:
            move_type = self.MOVE_TYPE_ADD
        elif move_type == self.MOVE_TYPE_ADD:
            move_type = self.MOVE_TYPE_REMOVE
        elif move_type == self.MOVE_TYPE_MOVE:
            dest, new_dest = new_dest, dest
        self.make_move(move_type, origin, dest, new_dest)

    def can_make_move(self, move_type, origin, dest, new_dest):
        # If the origin and destination is the same, the move won't be allowed anyway
        if origin == dest:
            return False

        result = True

        # We're trying to add an edge
        if move_type == self.MOVE_TYPE_ADD:
            # Make sure the edge doesn't already exist
            if self.graph.has_edge(origin, dest):
                result = False
        # We're trying to remove an edge
        elif move_type == self.MOVE_TYPE_REMOVE:
            # Make sure the edge exist
            if not self.graph.has_edge(origin, dest):
                result = False
        # We're trying to move an edge
        elif move_type == self.MOVE_TYPE_MOVE:
            # We shouldn't be allowed to move an edge to itself
            if dest == new_dest or origin == new_dest:
                return False
            # Make sure it's allowed to add an edge
            if not self.can_make_move(self.MOVE_TYPE_ADD, origin, new_dest, None):
                result = False
            # Make sure it's allowed to remove the specific edge
            elif not self.can_make_move(self.MOVE_TYPE_REMOVE, origin, dest, None):
                result = False

        return result

    def graph_is_valid(self, move_type, origin, dest, new_dest=None):
        # If we're adding an edge we don't need to check it
        if move_type == self.MOVE_TYPE_ADD:
            return True
        # If we're removing an edge we must make sure the old nodes are still connected
        elif move_type == self.MOVE_TYPE_REMOVE:
            return Analytics.is_nodes_connected(self.graph, origin, dest)
        # If we're moving an edge we must make sure the old nodes are still connected
        elif move_type == self.MOVE_TYPE_MOVE:
            return Analytics.is_nodes_connected(self.graph, origin, dest)

    print_iter = 10

    def print_state(self):
        if self.print_iter > 0:
            self.print_iter -= 1
        else:
            print(self.temperature)
            print(self.energy)
            Visual.draw(self.graph)
            self.print_iter = 10
