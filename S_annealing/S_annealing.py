# Python class for optimizing distributed consensus averaging using Simulated Annealing
# Written by Oskar Hahr & Johan Niklasson
import networkx as nx
import extended_networkx_tools as ext
from Greedy import Greedy
import random
import math


class Annealing_solver:
    current_graph = None
    convergence_rate = None
    adjacency_matrix = None
    row_length = None
    temperature = 10000
    rate_of_change = 0

    # The initialization function for the annealing solver object takes a networkx object as input
    # and function returns an "empty" annealing solver object
    def __init__(self, g):
        pass

    # The solve function takes an undirected networkx graph, containing no edges as input.
    # The function then creates a path through the graph to ensure that it is connected, afterwards
    # the simulated annealing algorithm is used to optimize the graph topology in regards to distributed
    # consensus reaching. The function returns the optimized networkx object. 
    def solve(self, g):

        # initialize function variables
        self.current_graph = ext.Solver.path(g)
        self.convergence_rate = ext.Analytics.convergence_rate(g)
        self.adjacency_matrix = ext.Analytics.get_neighbour_matrix(g)
        row_length = len(self.current_graph.nodes())


        while 0.001 < self.temperature:
            # perform 1000 iterations at each temperature
            for i in range(0,1000):
                # Select random {x,y} in the adjacency matrix.
                # The algorithm will depend to remove or add an edge between the nodes
                # x & y depending on if there already exists an edge or not connecting them
                x = random.randint(0, row_length - 1)
                y = random.randint(0, row_length - 1)
                move_type = self.adjacency_matrix[x][y]

                # Check if the proposed moved is valid or not.
                # If the move is invalid, continue otherwise evaluate the move
                if not self.make_move(x, y, move_type):
                    continue
                # If the move is a valid move, evaluate wether to keep it or not
                if not self.evaluate_move(x, y, move_type):
                    self.revert_move(x, y, move_type)
                else:
                    self.save_move(x, y, move_type)
            # After each 1000 iterations, the algorithm updates the temperature
            self.update_temperature()
        
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
    def evaluate_move(self, x, y, move_type):

        # Fetch the new convergence rate for the graph
        new_convergence = ext.Analytics.convergence_rate(self.current_graph)
        
        # If the new convergence rate is an improvement, the move is always saved.
        if new_convergence < self.convergence_rate:
            return True
        
        # Otherwise calculate the energy level, if the temperature is high the system is 
        # more inclined to keeping all changes. When the temperature "cools" the algorithm
        # becomes less and less inclined to keep changes that result in a regression in convergence rate.   
        e = math.exp(-(new_convergence - self.convergence_rate) / self.temperature)

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
            self.convergence_rate = ext.Analytics.convergence_rate(self.current_graph)
        
        if move_type == 1:
            self.adjacency_matrix[x][y] = 0
            self.adjacency_matrix[y][x] = 0
            self.convergence_rate = ext.Analytics.convergence_rate(self.current_graph)
    # The temperature decrements by a factor of 0.92 after each 1000 iterations
    def update_temperature(self):
        self.temperature = self.temperature * 0.92