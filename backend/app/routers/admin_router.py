import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas, auth, models
from ..services.alist_sync import trigger_source_sync
from ..services.random_pool import random_pool

router = APIRouter(prefix="/admin", tags=["Management API"])

# ==================== Dashboard ====================
@router.get("/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_dashboard_stats(db)


# ==================== Sources & Sync ====================
@router.get("/sources", response_model=List[schemas.StorageSourceResponse])
def list_sources(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_sources(db)

@router.post("/sources", response_model=schemas.StorageSourceResponse)
def add_source(
    source_in: schemas.StorageSourceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    return crud.create_source(db, source_in)

@router.post("/sources/{source_id}/sync")
async def sync_source(
    source_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    src = crud.get_source(db, source_id)
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")
    
    async def task_wrapper(s_id: int):
        await trigger_source_sync(s_id)
        random_pool.reload_from_db()

    background_tasks.add_task(task_wrapper, source_id)
    return {"message": f"Sync task scheduled in background for source '{src.name}'"}


# ==================== Images ====================
@router.get("/images")
def list_images(
    skip: int = 0,
    limit: int = 50,
    tag: Optional[str] = None,
    source_id: Optional[int] = None,
    orientation: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    images, total = crud.get_images(db, skip, limit, tag, source_id, orientation, is_active)
    return {
        "total": total,
        "items": [
            {
                "id": img.id,
                "raw_url": img.raw_url,
                "file_path": img.file_path,
                "filename": img.filename,
                "file_size": img.file_size,
                "width": img.width,
                "height": img.height,
                "orientation": img.orientation,
                "is_active": img.is_active,
                "view_count": img.view_count,
                "created_at": img.created_at,
                "tags": [t.name for t in img.tags]
            } for img in images
        ]
    }

@router.post("/images/batch-tag")
def batch_tag_images(
    req: schemas.ImageBatchTagRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    count = crud.batch_update_tags(db, req.image_ids, req.add_tags, req.remove_tags)
    random_pool.reload_from_db(db)
    return {"updated_count": count}


# ==================== API Keys ====================
@router.get("/keys", response_model=List[schemas.ApiKeyResponse])
def list_keys(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    keys = crud.get_api_keys(db, owner_id=None if current_user.is_admin else current_user.id)
    res = []
    for k in keys:
        res.append(schemas.ApiKeyResponse(
            id=k.id,
            key=k.key,
            name=k.name,
            allowed_tags_and=json.loads(k.allowed_tags_and or "[]"),
            allowed_tags_or=json.loads(k.allowed_tags_or or "[]"),
            blocked_tags=json.loads(k.blocked_tags or "[]"),
            orientation_filter=k.orientation_filter or "all",
            rate_limit_qpm=k.rate_limit_qpm,
            daily_quota=k.daily_quota,
            referer_whitelist=json.loads(k.referer_whitelist or "[]"),
            ip_whitelist=json.loads(k.ip_whitelist or "[]"),
            total_calls=k.total_calls or 0,
            is_active=k.is_active,
            created_at=k.created_at,
            last_used_at=k.last_used_at
        ))
    return res

@router.post("/keys", response_model=schemas.ApiKeyResponse)
def create_key(
    key_in: schemas.ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    k = crud.create_api_key(db, key_in, owner_id=current_user.id)
    return schemas.ApiKeyResponse(
        id=k.id,
        key=k.key,
        name=k.name,
        allowed_tags_and=json.loads(k.allowed_tags_and or "[]"),
        allowed_tags_or=json.loads(k.allowed_tags_or or "[]"),
        blocked_tags=json.loads(k.blocked_tags or "[]"),
        orientation_filter=k.orientation_filter or "all",
        rate_limit_qpm=k.rate_limit_qpm,
        daily_quota=k.daily_quota,
        referer_whitelist=json.loads(k.referer_whitelist or "[]"),
        ip_whitelist=json.loads(k.ip_whitelist or "[]"),
        total_calls=k.total_calls or 0,
        is_active=k.is_active,
        created_at=k.created_at,
        last_used_at=k.last_used_at
    )

@router.delete("/keys/{key_id}")
def delete_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    success = crud.delete_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"message": "API key deleted"}
