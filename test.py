import Greedy
import S_annealing
import extended_networkx_tools as ext
import networkx

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

class Test:
    x = ext.Creator.from_spec(v, e)
    annealing_solver = S_annealing.Annealing_solver(x)
    x = annealing_solver.solve_by_moves_only(x)
    distribution = ext.Analytics.get_distance_distribution(x)
    ext.Visual.draw(x)
    print(ext.Analytics.convergence_rate(x))
    print(distribution)