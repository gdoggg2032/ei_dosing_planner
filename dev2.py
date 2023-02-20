

import json
import pprint
from collections import defaultdict

from ortools.linear_solver import pywraplp

plan = {
    'environment': {
        'volume': 118.7,  # L
    },
    'solutions': [
        {
            'name': 'kno3',  # molecular weight = 101.1032
            'components': {
                'k': 39.0983 / 101.1032,
                'n': 14.0067 / 101.1032,
            }
        },
        {
            'name': 'kh2po4',  # molecular weight = 136.085542
            'components': {
                'k': 39.0983 / 136.085542,
                'p': 30.973762 / 136.085542,
            }
        },
        {
            'name': 'seachem_iron',
            'components': {
                'fe': 0.01,  # from https://www.seachem.com/flourish-iron.php
            }
        },
    ],
    'containers': [
        {
            'name': 'macro',
            'solutions': [
                'kno3',
                'kh2po4',
            ],
            'volume': 1000.0  # ml
        },
        {
            'name': 'micro',
            'solutions': [
                'seachem_iron',
            ],
            'volume': 1000.0  # ml
        },
    ],
    'schedule': [
        {'name': 'macro', 'dose': 10},  # Monday, 10ml
        {'name': 'micro', 'dose': 10},  # Tuesday, 10ml
        {'name': 'macro', 'dose': 10},  # Wednesday, 10ml
        {'name': 'micro', 'dose': 10},  # Thursday, 10ml
        {'name': 'macro', 'dose': 10},  # Friday, 10ml
        {'name': 'micro', 'dose': 10},  # Saturday, 10ml
    ],
    'constraints': [
        {'name': 'n', 'min': 1.7, 'max': 1.9},  # ppm
        {'name': 'p', 'min': 1.1, 'max': 1.2},  # ppm
        {'name': 'k', 'min': 5.0, 'max': 8.0},  # ppm
        {'name': 'fe', 'min': 0.1, 'max': 2.0},  # ppm
    ]
}


def optimize_plan(plan):
    pprint.pprint(plan)

    # build component_solution_dict
    component_solution_dict = defaultdict(dict)
    for solution in plan['solutions']:
        for component_name, concentration in solution['components'].items():
            component_solution_dict[component_name][solution['name']] = concentration  # percentage

    # summarize scheduled dose for each container
    container_dose = defaultdict(float)
    for dose in plan['schedule']:
        container_name = dose['name']
        container_dose[container_name] += dose['dose']  # ml

    # create solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    print(solver)

    # create variables
    container_solution_vars = defaultdict(dict)
    for container in plan['containers']:
        container_name = container["name"]
        for solution_name in container['solutions']:
            var_name = f'{solution_name}_in_{container_name}(g)'
            variable = solver.IntVar(0, solver.infinity(), var_name)
            container_solution_vars[container_name][solution_name] = variable

    # add constraints
    component_effect_dict = dict()
    for constraint in plan['constraints']:
        component_name = constraint['name']
        if not component_name in component_solution_dict:
            # no solutions contain this component
            assert constraint['min'] <= 0, f'cannot fit this constraint, {json.dumps(constraint)}'
        # get the effect of the component
        total_component_effect = 0.0
        for container in plan['containers']:
            container_name = container["name"]
            for solution_name in container['solutions']:
                if not solution_name in component_solution_dict[component_name]:
                    continue
                # get the whole addtional concentration
                component_concentration = component_solution_dict[component_name][solution_name]
                solution_var = container_solution_vars[container_name][solution_name]
                solution_dose = solution_var * container_dose[container_name] / container['volume']  # g
                component_dose = solution_dose * component_concentration  # g
                environment_effect = component_dose * 1000 / plan['environment']['volume']  # ppm
                total_component_effect += environment_effect
        # add constraint
        solver.Add(total_component_effect >= constraint['min'])
        solver.Add(total_component_effect <= constraint['max'])
        component_effect_dict[component_name] = total_component_effect

    # objective function: minimize usage of all solutions
    total_usage = 0
    for container_name in container_solution_vars:
        for solution_name in container_solution_vars[container_name]:
            total_usage += container_solution_vars[container_name][solution_name]
    solver.Minimize(total_usage)

    # info
    print('Number of variables =', solver.NumVariables())
    print('Number of constraints =', solver.NumConstraints())

    # solve
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('solution:')
        print('total usage =', solver.Objective().Value())
        print('plan:')
        for container_name in container_solution_vars:
            print(f'container: {container_name}')
            for solution_name in container_solution_vars[container_name]:
                variable = container_solution_vars[container_name][solution_name]
                print(f'{solution_name} = {variable.solution_value()}(g)')

        print('effect:')
        for component_name in component_effect_dict:
            print(f'{component_name}: {component_effect_dict[component_name].solution_value()}')
    else:
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    optimize_plan(plan)
