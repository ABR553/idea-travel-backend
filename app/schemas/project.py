from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: str
    slug: str
    name: str
    tag_id: str

    model_config = {"populate_by_name": True}


class ProjectCreate(BaseModel):
    slug: str
    name: str
    tag_id: str
    link_template: str
