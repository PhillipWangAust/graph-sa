import Greedy
import S_annealing
import extended_networkx_tools as ext
import networkx

from S_annealing.annealing import Annealing

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
    g = ext.Creator.from_random(5)
    anneal = Annealing(g)
    g = anneal.solve()
    ext.Visual.draw(g)

    convergence_rate = ext.Analytics.convergence_rate(g)
    energy = ext.Analytics.total_edge_cost(g)
    distribution = networkx.eccentricity(g)

    print(convergence_rate)
    print(energy)
    print(distribution)

    exit(0)

class Test:
    x = ext.Creator.from_random(30)
    annealing_solver = S_annealing.Annealing_solver(x)
    x = annealing_solver.solve()
    distribution = ext.Analytics.get_distance_distribution(x)
    ext.Visual.draw(x)
    print(ext.Analytics.convergence_rate(x))
    print(distribution)