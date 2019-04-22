import networkx as nx
import extended_networkx_tools as ext


class Greedy:
    
    @staticmethod
    def greedy_solve(g):
        nodes = g.nodes()

        for edge in zip(nodes[:-1], nodes[1:]):
            for x, y in edge:
                ext.Creator.add_weighted_edge(g, x, y)
        
        assert nx.is_connected(g)

        return g


