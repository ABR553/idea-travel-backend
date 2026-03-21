from pydantic import BaseModel


class RouteStepResponse(BaseModel):
    day: int
    title: str
    description: str
    destination: str
