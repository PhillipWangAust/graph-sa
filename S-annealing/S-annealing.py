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

    def __init__(self, g):
        pass

    def solve(self, g):

        self.current_graph = Greedy.greedy_solve(g)
        self.convergence_rate = ext.Analytics.convergence_rate(g)
        self.adjacency_matrix = ext.Analytics.get_neighbour_matrix(g)
        row_length = len(self.current_graph.nodes())

        while True:
            x = random.randint(0, row_length - 1)
            y = random.randint(0, row_length - 1)
            move_type = self.adjacency_matrix[x][y]

            # if the move is invalid, continue
            if not self.make_move(x, y, move_type):
                continue
            # if the move was valid, evaluate if it is kept or not
            if not self.evaluate_move(x, y, move_type):
                self.revert_move(x, y, move_type)
            else:
                self.save_move(x, y, move_type)
            
            self.update_temperature()

    def make_move(self, x, y, move_type):
        if x == y:
            return False

        if move_type == 1:
            self.current_graph.remove_edge(x, y)
            if nx.is_connected(self.current_graph):
                return True

            else:
                ext.Creator.add_weighted_edge(self.current_graph, x, y)
                return False

        if move_type == 0:
            ext.Creator.add_weighted_edge(self.current_graph, x, y)
            return True
    
    def evaluate_move(self, x, y, move_type):
        new_convergence = ext.Analytics.convergence_rate(self.current_graph)
        
        if new_convergence < self.convergence_rate:
            return True
        
        e = math.exp((new_convergence - self.convergence_rate) / self.temperature)

        if random.randint(0,1) < e:
            return True
        
        return False

    def revert_move(self, x, y, move_type):
        if move_type == 0:
            self.current_graph.remove_edge(x,y)
        else:
            ext.Creator.add_weighted_edge(self.current_graph, x, y)

    def save_move(self, x, y, move_type):
        if move_type == 0:
            self.adjacency_matrix[x][y] = 1
            self.adjacency_matrix[y][x] = 1
            self.convergence_rate = ext.Analytics.convergence_rate(self.current_graph)
        
        if move_type == 1:
            self.adjacency_matrix[x][y] = 0
            self.adjacency_matrix[x][y] = 0
            self.convergence_rate = ext.Analytics.convergence_rate(self.current_graph)

    def update_temperature(self):
        self.temperature = self.temperature * 0.92