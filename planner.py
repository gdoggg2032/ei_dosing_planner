
import fire

from data_type import Plan
from util import optimize_containers, get_effects


class Planner:

    def optimize_containers(self,
                            input_path: str | None = './sample_plan.json',
                            output_path: str | None = 'solved_plan.json',
                            container_names: list[str] | None = None):
        print(f'container names: {container_names}')
        plan = Plan.parse_file(input_path)
        solved_plan = optimize_containers(plan,
                                          container_names=container_names,)
        with open(output_path, 'w') as file_obj:
            file_obj.write(solved_plan.json(indent=4))

    def compute_effects(self,
                        input_path: str | None = './sample_plan.json',
                        output_path: str | None = 'solved_plan.json',
                        ):
        plan = Plan.parse_file(input_path)
        # calculate effects
        effects = get_effects(plan)
        solved_plan = plan.copy(update=dict(effects=effects))
        with open(output_path, 'w') as file_obj:
            file_obj.write(solved_plan.json(indent=4))  
if __name__ == '__main__':
    fire.Fire(Planner)
