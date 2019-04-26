# Python class for optimizing distributed consensus averaging using Simulated Annealing
# Written by Oskar Hahr & Johan Niklasson
import networkx as nx
import extended_networkx_tools as ext
from Greedy import Greedy
import random
import math


class Annealing_solver:
    current_graph = None
    adjacency_matrix = None
    row_length = None
    energy_cost = None
    max_energy_cost = None

    temperature = 10000

    # The initialization function for the annealing solver object takes a networkx object as input
    # and function returns an "empty" annealing solver object
    def __init__(self, g):
        self.current_graph = g
        self.adjacency_matrix = ext.Analytics.get_neighbour_matrix(g)
        self.row_length = len(self.current_graph.nodes())
        self.max_energy_cost = ext.Analytics.hypothetical_max_edge_cost(g)
        self.energy_cost = self.get_energy(g)

    # The solve function takes an undirected networkx graph, containing no edges as input.
    # The function then creates a path through the graph to ensure that it is connected, afterwards
    # the simulated annealing algorithm is used to optimize the graph topology in regards to distributed
    # consensus reaching. The function returns the optimized networkx object. 
    def solve(self):

        # initialize function variables
        if not nx.is_connected(self.current_graph):
            self.current_graph = ext.Solver.path(self.current_graph)

        true_false = [True, False]

        while 0.001 < self.temperature:
            # perform 1000 iterations at each temperature
            for i in range(0, 100):
                # Select random {x,y} in the adjacency matrix.
                # The algorithm will depend to remove or add an edge between the nodes
                # x & y depending on if there already exists an edge or not connecting them
                x = random.randint(0, self.row_length - 1)
                y = random.randint(0, self.row_length - 1)
                move_type = self.adjacency_matrix[x][y]

                # Check if the proposed moved is valid or not.
                # If the move is invalid, continue otherwise evaluate the move
                if not self.make_move(x, y, move_type):
                    continue
                # If the move is a valid move, evaluate whether to keep it or not
                if not self.evaluate_move():
                    self.revert_move(x, y, move_type)
                else:
                    self.save_move(x, y, move_type)
                self.energy_cost = self.get_energy(self.current_graph)
            # After each 1000 iterations, the algorithm updates the temperature
            self.update_temperature()

        
        return self.current_graph

    def solve_by_moves_only(self):
        # initialize function variables
        if not nx.is_connected(self.current_graph):
            self.current_graph = ext.Solver.path(self.current_graph)

        nodes = list(self.current_graph.nodes)

        while 0.001 < self.temperature:
            for i in range(0, 200):
                # Get a random start node
                origin = random.choice(nodes)
                # Get a random edge from the node
                edge = random.choice(list(self.current_graph.edges(origin)))
                # Get the old destination node
                old_dest = edge[1]

                # Randomise a new destination
                new_dest = random.choice(nodes)

                # Make sure the new destination isn't the same as the origin or old destination
                if origin == new_dest or old_dest == new_dest or self.current_graph.has_edge(origin, new_dest):
                    continue

                # Move the edge point
                self.move_edge(origin, old_dest, new_dest)

                # If ok this far, make sure the graph is still one component
                still_connected = ext.Analytics.is_nodes_connected(self.current_graph, origin, old_dest)
                # If not, make the move illegal
                if still_connected is False:
                    revert_move = True
                else:
                    # Check if the move was good. If not, revert the move
                    revert_move = self.evaluate_move() is False

                if revert_move:
                    self.move_edge(origin, new_dest, old_dest)

            # Update the temp
            self.update_temperature()
            self.energy_cost = self.get_energy(self.current_graph)
        return self.current_graph


    # make_move is a function to  check if the algorithm is attempting to perform
    # an invalid/valid move. The function takes two coordinates representing nodes in a graph, 
    # & a move_type: {0: add edge, 1: remove edge}. The function outputs a boolean True/False,
    # depending on if the move was valid/invalid respectively.
    def make_move(self, x, y, move_type):

        # If x = y the move is invalid due to attempting to add a looping edge,
        if x == y:
            return False
        # If move_type = 1 the algorithm is trying to remove an edge,
        # check if removing the edge disconnects the graph if so it is an invalid move.
        if move_type == 1:
            self.current_graph.remove_edge(x, y)
            if ext.Analytics.is_nodes_connected(self.current_graph, x, y):
                return True
            # If graph was disconnected by removing the edge, re-add it and return false
            else:
                ext.Creator.add_weighted_edge(self.current_graph, x, y)
                return False
        # Adding an edge is always a valid move
        if move_type == 0:
            ext.Creator.add_weighted_edge(self.current_graph, x, y)
            return True
    
    # evaluate_move is a function used to check if a move is to be saved or reverted
    # based on the change in energy level that the move provided.
    def evaluate_move(self):

        # Fetch the new energy cost for the graph
        new_energy_cost = self.get_energy(self.current_graph)
        
        # If the new energy is an improvement, the move is always saved.
        if new_energy_cost < self.energy_cost:
            return True

        # Otherwise calculate the energy level, if the temperature is high the system is 
        # more inclined to keeping all changes. When the temperature "cools" the algorithm
        # becomes less and less inclined to keep changes that result in a regression in energy cost.
        e = math.exp(-(new_energy_cost - self.energy_cost) / self.temperature)

        # Pick a random float number between 0 and 1, if the variable e is larger than the random
        # number, we keep the change otherwise we revert it.
        if random.uniform(0,1) < e:
            return True
        
        return False
    
    # The function to revert a move that has been made. The function takes two coordinates representing positions
    # in the adjacency matrix, as well as a move_type:{0: an edge was added or 1: an edge was removed}.
    def revert_move(self, x, y, move_type):
        if move_type == 0:
            self.current_graph.remove_edge(x,y)
        else:
            ext.Creator.add_weighted_edge(self.current_graph, x, y)

    # Function to save a move that was made. The function takes two coordinates representing positions in
    # the adjacency matrix & a move_type:{0: an edge was added or 1: an edge was removed}. 
    def save_move(self, x, y, move_type):
        if move_type == 0:
            self.adjacency_matrix[x][y] = 1
            self.adjacency_matrix[y][x] = 1
            self.energy_cost = self.get_energy(self.current_graph)
        
        if move_type == 1:
            self.adjacency_matrix[x][y] = 0
            self.adjacency_matrix[y][x] = 0
            self.energy_cost = self.get_energy(self.current_graph)

    temp_iterations = 0
    # The temperature decrements by a factor of 0.92 after each 1000 iterations
    def update_temperature(self):
        self.temperature = self.temperature * 0.92
        self.temp_iterations += 1
        if self.temp_iterations > 10:
            print("Temp: " + str(self.temperature))
            print("Energy: " + str(self.energy_cost))
            print("Converge: " + str(ext.Analytics.convergence_rate(self.current_graph)))
            self.temp_iterations = 0
            ext.Visual.draw(self.current_graph)

    def get_energy(self, g):
        convergence_rate = ext.Analytics.convergence_rate(g)
        edge_cost = ext.Analytics.total_edge_cost(g)
        edge_percentage = edge_cost / self.max_energy_cost
        return edge_cost
        if convergence_rate == 1.0:
            return math.inf
        return edge_cost/(-math.log(convergence_rate))

    def isclose(self, a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    def move_edge(self, origin, old_dest, new_dest):
        if origin == new_dest or old_dest == new_dest:
            return False
        if not self.current_graph.has_edge(origin, old_dest):
            return False
        if self.current_graph.has_edge(origin, new_dest):
            return False

        self.current_graph.remove_edge(origin, old_dest)
        ext.Creator.add_weighted_edge(self.current_graph, origin, new_dest)
