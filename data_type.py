from pydantic import BaseModel


class Environment(BaseModel):
    volume: float  # L, tank water volume


class Solution(BaseModel):
    name: str
    components: dict[str, float]  # substance to concentration(%)
    price_per_g: float | None = 1e-6


class Container(BaseModel):
    name: str
    solutions: dict[str, float | None]  # solution name to weight(g)
    volume: float  # ml


class Dose(BaseModel):
    name: str  # container name
    dose: float  # ml


class ComponentConstraint(BaseModel):
    name: str  # component name
    min: float  # ppm in tank
    max: float  # ppm in tank


class SolutionConstraint(BaseModel):
    name: str  # solution name
    uniform: bool  # uniform distribution in all containers


class Effect(BaseModel):
    name: str  # component name
    concentration: float  # ppm


class Plan(BaseModel):
    name: str
    comment: str
    price: float | None = 0
    environment: Environment
    solutions: list[Solution]
    containers: list[Container]
    schedule: list[Dose]
    component_constraints: list[ComponentConstraint]
    solution_constraints: list[SolutionConstraint]
    effects: list[Effect]
