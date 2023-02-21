

import json
from collections import defaultdict

from ortools.linear_solver import pywraplp

from data_type import Container, Effect, Plan


def get_effects(plan: Plan) -> list[Effect]:

    # build solution_component_dict
    solution_component_dict = defaultdict(dict)
    for solution in plan.solutions:
        for component_name, concentration in solution.components.items():
            solution_component_dict[solution.name][component_name] = concentration  # percentage

    # summarize scheduled dose for each container
    container_dose = defaultdict(float)
    for dose in plan.schedule:
        container_name = dose.name
        container_dose[container_name] += dose.dose  # ml

    total_component_effect = defaultdict(float)

    for container in plan.containers:
        for solution_name, usage in container.solutions.items():
            for component_name, component_concentration in solution_component_dict[solution_name].items():
                # get the whole addtional concentration
                solution_dose = usage * container_dose[container.name] / container.volume  # g
                component_dose = solution_dose * component_concentration  # g
                environment_effect = component_dose * 1000 / plan.environment.volume  # ppm
                total_component_effect[component_name] += environment_effect
    effects = []
    for component_name, concentration in total_component_effect.items():
        effect = Effect(name=component_name, concentration=concentration)
        effects.append(effect)
    return sorted(effects, key=lambda x: x.concentration, reverse=True)  # rank by concentration


def optimize_containers(plan: Plan) -> Plan:

    # build component_solution_dict
    component_solution_dict = defaultdict(dict)
    for solution in plan.solutions:
        for component_name, concentration in solution.components.items():
            component_solution_dict[component_name][solution.name] = concentration  # percentage

    # summarize scheduled dose for each container
    container_dose = defaultdict(float)
    for dose in plan.schedule:
        container_name = dose.name
        container_dose[container_name] += dose.dose  # ml

    # create solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    print(solver)

    # create variables
    container_solution_vars = defaultdict(dict)
    for container in plan.containers:
        container_name = container.name
        for solution_name in container.solutions:
            var_name = f'{solution_name}_in_{container_name}(g)'
            variable = solver.IntVar(0, solver.infinity(), var_name)
            container_solution_vars[container_name][solution_name] = variable

    # add constraints
    component_effect_dict = dict()
    for constraint in plan.constraints:
        component_name = constraint.name
        if not component_name in component_solution_dict:
            # no solutions contain this component
            assert constraint.min <= 0, f'cannot fit this constraint, {json.dumps(constraint)}'
        # get the effect of the component
        total_component_effect = 0.0
        for container in plan.containers:
            for solution_name in container.solutions:
                if not solution_name in component_solution_dict[component_name]:
                    continue
                # get the whole addtional concentration
                component_concentration = component_solution_dict[component_name][solution_name]
                solution_var = container_solution_vars[container.name][solution_name]
                solution_dose = solution_var * container_dose[container.name] / container.volume  # g
                component_dose = solution_dose * component_concentration  # g
                environment_effect = component_dose * 1000 / plan.environment.volume  # ppm
                total_component_effect += environment_effect
        # add constraint
        solver.Add(total_component_effect >= constraint.min)
        solver.Add(total_component_effect <= constraint.max)
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

        solved_plan = plan.copy()
        solved_containers = []
        for container in plan.containers:
            print(f'container: {container.name}')
            solution_dict = dict()
            for solution_name in container_solution_vars[container.name]:
                variable = container_solution_vars[container.name][solution_name]
                print(f'{solution_name} = {variable.solution_value()}(g)')
                solution_dict[solution_name] = variable.solution_value()

            solved_containers.append(Container(name=container.name,
                                               solutions=solution_dict,
                                               volume=container.volume))
        solved_plan = plan.copy(update=dict(containers=solved_containers))
        # calculate effects
        effects = get_effects(solved_plan)
        solved_plan = solved_plan.copy(update=dict(effects=effects))
        return solved_plan
    else:
        print('The problem does not have an optimal solution.')


def main():
    plan = Plan.parse_file('sample_plan.json')
    solved_plan = optimize_containers(plan)
    with open('solved_plan.json', 'w') as file_obj:
        file_obj.write(solved_plan.json(indent=4))


if __name__ == '__main__':
    main()
