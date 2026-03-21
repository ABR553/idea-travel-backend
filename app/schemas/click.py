from pydantic import BaseModel


class ClickResponse(BaseModel):
    message: str
    entity_type: str
    entity_id: str
