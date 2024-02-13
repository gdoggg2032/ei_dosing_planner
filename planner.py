

import fire
import tomlkit

from data_type import Plan
from util import get_effects, optimize_containers


class Planner:

    def optimize_containers(self,
                            input_path: str | None = './sample_plan.toml',
                            output_path: str | None = 'solved_plan.toml',
                            container_names: list[str] | None = None):
        print(f'container names: {container_names}')
        with open(input_path, 'r') as file_obj:
            raw_dict = tomlkit.load(file_obj) # for preserve key order
            plan = Plan.parse_obj(raw_dict)
        solved_plan = optimize_containers(plan,
                                          container_names=container_names,)
        with open(output_path, 'w') as file_obj:
            output_dict = raw_dict
            output_dict.update(solved_plan.dict())
            tomlkit.dump(output_dict, file_obj)


    def compute_effects(self,
                        input_path: str | None = './sample_plan.toml',
                        output_path: str | None = 'solved_plan.toml',
                        ):
        with open(input_path, 'r') as file_obj:
            raw_dict = tomlkit.load(file_obj) # for preserve key order
            plan = Plan.parse_obj(raw_dict)
        # calculate effects
        effects = get_effects(plan)
        solved_plan = plan.copy(update=dict(effects=effects))
        with open(output_path, 'w') as file_obj:
            output_dict = raw_dict
            output_dict.update(solved_plan.dict())
            tomlkit.dump(solved_plan.dict(), file_obj)

if __name__ == '__main__':
    fire.Fire(Planner)
