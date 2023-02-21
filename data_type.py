

from pydantic import BaseModel, validator


class Environment(BaseModel):
    volume: float  # L, tank water volume


class Solution(BaseModel):
    name: str
    components: dict[str, float]  # substance to concentration(%)

    @validator('components')
    def check_component_percentage(cls, v):
        if sum(v.values()) > 1:
            raise ValueError('sum of component percentages > 1')
        return v


class Container(BaseModel):
    name: str
    solutions: dict[str, float | None]  # solution name to weight(g)
    volume: float  # ml


class Dose(BaseModel):
    name: str  # container name
    dose: float  # ml


class Constraint(BaseModel):
    name: str  # component name
    min: float  # ppm in tank
    max: float  # ppm in tank


class Effect(BaseModel):
    name: str  # component name
    concentration: float  # ppm


class Plan(BaseModel):
    name: str
    environment: Environment
    solutions: list[Solution]
    containers: list[Container]
    schedule: list[Dose]
    constraints: list[Constraint]
    effects: list[Effect]
