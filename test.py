import simulated_annealing
import extended_networkx_tools as ext

from simulated_annealing.annealing2 import Annealing2

# Make sure this file only runs when executed
if __name__ == "__main__":

    v = {
        0: (-2, 1),
        1: (-2, -1),
        2: (-1, 0),

        3: (2, 1),
        4: (2, -1),
        5: (1, 0),
    }

    e = {
        2: [0, 1, 5],
        5: [3, 4],
    }

    if True:
        g = ext.Creator.from_spec(v, e)
        ext.Visual.draw(g)
        anneal = Annealing2(g, iterations=(len(g.nodes) * len(g.nodes)))
        anneal.set_energy_function('edge_cost')
        g = anneal.solve(True)
        ext.Visual.draw(g)

        convergence_rate = ext.Analytics.convergence_rate(g)
        energy = ext.Analytics.total_edge_cost(g)
        distribution = ext.Analytics.get_eccentricity_distribution(g)

        print(convergence_rate)
        print(energy)
        print(distribution)

        exit(0)

    class Test:
        x = ext.Creator.from_random(30)
        annealing_solver = simulated_annealing.Annealing1(x)
        x = annealing_solver.solve()
        distribution = ext.Analytics.get_distance_distribution(x)
        ext.Visual.draw(x)
        print(ext.Analytics.convergence_rate(x))
        print(distribution)