

import fire
import tomllib
import tomli_w

from collections import OrderedDict
from data_type import Plan
from util import get_effects, optimize_containers


class Planner:

    def optimize_containers(self,
                            input_path: str | None = './sample_plan.toml',
                            output_path: str | None = 'solved_plan.toml',
                            container_names: list[str] | None = None):
        print(f'container names: {container_names}')
        with open(input_path, 'rb') as file_obj:
            plan = Plan.model_validate(tomllib.load(file_obj))
        solved_plan = optimize_containers(plan,
                                          container_names=container_names,)
        with open(output_path, 'wb') as file_obj:
            output_dict = solved_plan.model_dump()
            ordered_dict = OrderedDict((field, output_dict.get(field)) for field in solved_plan.model_fields)
            tomli_w.dump(ordered_dict, file_obj, multiline_strings=True)


    def compute_effects(self,
                        input_path: str | None = './sample_plan.toml',
                        output_path: str | None = 'solved_plan.toml',
                        ):
        with open(input_path, 'rb') as file_obj:
            # raw_dict = tomllib.load(file_obj) # for preserve key order
            plan = Plan.model_validate(tomllib.load(file_obj))
        # calculate effects
        effects = get_effects(plan)
        solved_plan = plan.model_copy(update=dict(effects=effects))
        with open(output_path, 'wb') as file_obj:
            output_dict = solved_plan.model_dump()
            ordered_dict = OrderedDict((field, output_dict.get(field)) for field in solved_plan.model_fields)
            tomli_w.dump(ordered_dict, file_obj, multiline_strings=True)

if __name__ == '__main__':
    fire.Fire(Planner)
