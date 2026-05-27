from fastapi import APIRouter, HTTPException
from app.schemas.material import MaterialCreate
from app.agents.tools.local_storage import LocalStorageTool

router = APIRouter(prefix="/api/materials", tags=["materials"])


@router.post("")
def create_material(payload: MaterialCreate):
    storage = LocalStorageTool()
    return storage.save_material(
        title=payload.title,
        content=payload.content,
        source_type=payload.source_type,
        source_name=payload.source_name,
        tags=payload.tags,
    )


@router.get("")
def list_materials():
    storage = LocalStorageTool()
    return storage.list_materials()


@router.get("/{material_id}")
def get_material(material_id: str):
    storage = LocalStorageTool()
    try:
        return storage.read_material(material_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Material not found")