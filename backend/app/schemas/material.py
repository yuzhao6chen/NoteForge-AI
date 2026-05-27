from pydantic import BaseModel


class MaterialCreate(BaseModel):
    title: str
    content: str
    source_type: str = "idea"
    source_name: str = ""
    tags: str = ""


class MaterialRead(BaseModel):
    id: int
    title: str
    content: str
    source_type: str
    source_name: str
    tags: str
    summary: str = ""

    class Config:
        from_attributes = True
