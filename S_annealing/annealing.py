import random
from typing import List

import math
import networkx as nx
from extended_networkx_tools import Creator, Analytics, Tools, Visual, Solver


class Annealing:

    MOVE_TYPE_ADD = 0
    MOVE_TYPE_REMOVE = 1
    MOVE_TYPE_MOVE = 2

    graph: nx.Graph
    max_edge_cost: float
    adjacency_matrix: List[List[float]]
    row_length: int

    temperature: float
    energy: float

    def __init__(self, nxg: nx.Graph):
        self.temperature = 10000
        self.graph = nxg
        self.max_edge_cost = Analytics.hypothetical_max_edge_cost(nxg)
        self.adjacency_matrix = Analytics.get_neighbour_matrix(nxg)
        self.row_length = len(self.adjacency_matrix)

    def update_temperature(self):
        self.temperature = self.temperature * 0.92

    def get_energy(self):
        convergence_rate = Analytics.convergence_rate(self.graph)
        edge_cost = Analytics.total_edge_cost(self.graph)
        edge_percentage = edge_cost / self.max_edge_cost
        return edge_cost

    def solve(self):
        # If the graph is not connected, just make a path of it
        if not nx.is_connected(self.graph):
            self.graph = Solver.path(self.graph)

        # Get the initial energy
        self.energy = self.get_energy()

        while 0.001 < self.temperature:
            for i in range(0, 200):
                origin = random.randint(0, self.row_length - 1)
                dest = random.randint(0, self.row_length - 1)
                new_dest = random.randint(0, self.row_length - 1)

                move_type = self.adjacency_matrix[origin][dest]
                #if move_type == self.MOVE_TYPE_REMOVE:
                #    if self.adjacency_matrix[origin][new_dest] == 0 and random.randint(0, 1) == 1:
                #        move_type = self.MOVE_TYPE_MOVE

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

            # Otherwise it worked and we can update the new energy
            self.energy = self.get_energy()
            # Update the temperature after the new graph
            self.update_temperature()
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
        else:
            return True

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