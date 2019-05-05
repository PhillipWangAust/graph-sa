import copy
import random

import math
import networkx as nx
from extended_networkx_tools import Creator, Analytics, Visual, Solver, AnalyticsGraph


class Annealing2:

    MOVE_TYPE_ADD = 0
    MOVE_TYPE_REMOVE = 1
    MOVE_TYPE_MOVE = 2

    graph: AnalyticsGraph
    """
    The current graph that is under work.
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
        # If the graph is not connected, just make a path of it, as we must have a
        # connected graph initially.
        if not nx.is_connected(nxg):
            nxg = Solver.path(nxg)
        # Set the provided graph
        self.graph = AnalyticsGraph(nxg)

        # Initialisation of the graph data
        self.temperature = start_temperature
        self.iterations = iterations

        # Default energy function
        self._optimization_function = self.fn_energy_combined

    @staticmethod
    def fn_energy_convergence_rate(ag: AnalyticsGraph):
        return ag.get_convergence_rate()

    @staticmethod
    def fn_energy_edge_cost(ag: AnalyticsGraph):
        return ag.get_edge_cost()

    @staticmethod
    def fn_energy_combined(ag: AnalyticsGraph):
        convergence_rate = ag.get_convergence_rate()
        edge_cost = ag.get_edge_cost()
        if convergence_rate == 1.0:
            return math.inf
        if convergence_rate == 0:
            convergence_rate = 1e-8
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

    def solve(self, visualise=False, solve_for_nodes=None):

        best_graph = copy.deepcopy(self.graph)
        best_energy = math.inf

        if solve_for_nodes is None:
            solve_for_nodes = list(self.graph.graph().nodes)

        # Get the initial energy
        self.energy = self.get_energy()

        while 0.001 < self.temperature:
            for i in range(0, self.iterations):
                origin = solve_for_nodes[random.randint(0, len(solve_for_nodes) - 1)]
                dest = random.randint(0, self.graph.get_dimension() - 1)
                new_dest = random.randint(0, self.graph.get_dimension() - 1)

                move_type = self.graph.get_adjacency_matrix_sa()[origin][dest]
                if move_type == self.MOVE_TYPE_REMOVE:
                    if self.graph.get_adjacency_matrix_sa()[origin][new_dest] == 0 and random.randint(0, 1) == 1:
                        move_type = self.MOVE_TYPE_MOVE

                if move_type == self.MOVE_TYPE_ADD:
                    if not self.graph.add_edge(origin, dest):
                        continue
                elif move_type == self.MOVE_TYPE_REMOVE:
                    if not self.graph.remove_edge(origin, dest):
                        continue
                elif move_type == self.MOVE_TYPE_MOVE:
                    if not self.graph.move_edge(origin, dest, new_dest):
                        continue

                if not self.graph.is_connected():
                    self.graph.revert()
                    continue
                if not self.evaluate_state():
                    self.graph.revert()
                    continue

                self.energy = self.get_energy()
                # Make sure we keep the best state of the graph
                if self.energy < best_energy:
                    best_graph = copy.deepcopy(self.graph)
                    best_energy = self.energy

            # Revert to keep the best graph
            self.graph = copy.deepcopy(best_graph)
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

    print_iter = 10

    def print_state(self):
        if self.print_iter > 0:
            self.print_iter -= 1
        else:
            print(self.temperature)
            print(self.energy)
            Visual.draw(self.graph.graph())
            self.print_iter = 10
