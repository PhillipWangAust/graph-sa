import Greedy
import S_annealing
import extended_networkx_tools as ext
import networkx

class Test:
    x = ext.Creator.from_random(100)
    annealing_solver = S_annealing.Annealing_solver(x)
    x = annealing_solver.solve(x)
    ext.Visual.draw(x)
    print(ext.Analytics.convergence_rate(x))
