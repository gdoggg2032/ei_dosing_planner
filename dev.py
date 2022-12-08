
from collections import defaultdict

from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('SCIP')
print(solver)

VOL = 118.7
DOSE_VOL = 450
N_DOSE = 3
MAX_DOSE = DOSE_VOL // N_DOSE

# ppm
N_min = 1.7
N_max = 1.9
K_min = 5
K_max = 8
P_min = 1.1
P_max = 1.2

# KNO3
solution_dict = dict()


solution_dict['kno3'] = solver.IntVar(0, MAX_DOSE, 'kno3_dose_ml') * N_DOSE
solution_dict['kh2po4'] = solver.IntVar(0, MAX_DOSE, 'kh2po4_dose_ml') * N_DOSE


ingredient_dict = defaultdict(float)

# ppm
ingredient_dict['n@kno3'] = solution_dict['kno3'] / VOL * 22.8713
ingredient_dict['k@kno3'] = solution_dict['kno3'] / VOL * 63.7128

ingredient_dict['k@kh2po4'] = solution_dict['kh2po4'] / VOL * 7.1691
ingredient_dict['p@kh2po4'] = solution_dict['kh2po4'] / VOL * 5.6985


print('Number of variables =', solver.NumVariables())

# constraints

# Constraint N range
total_n = ingredient_dict['n@kno3']
solver.Add(total_n >= N_min)
solver.Add(total_n <= N_max)

# Constraint K range
total_k = ingredient_dict['k@kno3'] + ingredient_dict['k@kh2po4']
solver.Add(total_k >= K_min)
solver.Add(total_k <= K_max)

# Constraint N range
total_p = ingredient_dict['p@kh2po4']
solver.Add(total_p >= P_min)
solver.Add(total_p <= P_max)

print('Number of constraints =', solver.NumConstraints())


# Objective function: minimize dose
solver.Minimize(solution_dict['kno3'] + solution_dict['kh2po4'])

status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
    print('x =', solution_dict['kno3'].solution_value())
    print('y =', solution_dict['kh2po4'].solution_value())
else:
    print('The problem does not have an optimal solution.')
