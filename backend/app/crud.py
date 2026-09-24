import json
import secrets
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from . import models, schemas
from .auth import get_password_hash

# ==================== User CRUD ====================
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    if user_update.username is not None:
        db_user.username = user_update.username
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# ==================== StorageSource CRUD ====================
def get_sources(db: Session) -> List[models.StorageSource]:
    return db.query(models.StorageSource).all()

def get_source(db: Session, source_id: int) -> Optional[models.StorageSource]:
    return db.query(models.StorageSource).filter(models.StorageSource.id == source_id).first()

def create_source(db: Session, source_in: schemas.StorageSourceCreate) -> models.StorageSource:
    db_source = models.StorageSource(
        name=source_in.name,
        base_url=source_in.base_url.rstrip("/"),
        root_path=source_in.root_path,
        token=source_in.token,
        auto_sync_interval=source_in.auto_sync_interval
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

def update_source(db: Session, source_id: int, source_update: schemas.StorageSourceUpdate) -> Optional[models.StorageSource]:
    db_source = get_source(db, source_id)
    if not db_source:
        return None
    data = source_update.model_dump(exclude_unset=True)
    if "base_url" in data and data["base_url"]:
        data["base_url"] = data["base_url"].rstrip("/")
    for k, v in data.items():
        setattr(db_source, k, v)
    db.commit()
    db.refresh(db_source)
    return db_source

def delete_source(db: Session, source_id: int) -> bool:
    db_source = get_source(db, source_id)
    if db_source:
        db.delete(db_source)
        db.commit()
        return True
    return False


# ==================== Tag CRUD ====================
def get_or_create_tag(db: Session, name: str) -> models.Tag:
    clean_name = name.strip()
    tag = db.query(models.Tag).filter(models.Tag.name == clean_name).first()
    if not tag:
        tag = models.Tag(name=clean_name, slug=clean_name.lower())
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag

def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tag]:
    return db.query(models.Tag).order_by(desc(models.Tag.image_count)).offset(skip).limit(limit).all()


# ==================== Image CRUD ====================
def get_images(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    tag: Optional[str] = None,
    source_id: Optional[int] = None,
    orientation: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[models.Image], int]:
    query = db.query(models.Image)
    if source_id is not None:
        query = query.filter(models.Image.source_id == source_id)
    if orientation is not None and orientation != "all":
        query = query.filter(models.Image.orientation == orientation)
    if is_active is not None:
        query = query.filter(models.Image.is_active == is_active)
    if tag:
        query = query.filter(models.Image.tags.any(models.Tag.name == tag))
    
    total = query.count()
    images = query.order_by(desc(models.Image.id)).offset(skip).limit(limit).all()
    return images, total

def get_image(db: Session, image_id: int) -> Optional[models.Image]:
    return db.query(models.Image).filter(models.Image.id == image_id).first()

def get_image_by_filepath(db: Session, file_path: str) -> Optional[models.Image]:
    return db.query(models.Image).filter(models.Image.file_path == file_path).first()

def create_or_update_image(db: Session, img_in: schemas.ImageCreate, source_id: Optional[int] = None) -> models.Image:
    existing = get_image_by_filepath(db, img_in.file_path)
    if existing:
        existing.raw_url = img_in.raw_url
        existing.filename = img_in.filename or existing.filename
        existing.file_size = img_in.file_size or existing.file_size
        existing.mime_type = img_in.mime_type or existing.mime_type
        existing.width = img_in.width or existing.width
        existing.height = img_in.height or existing.height
        existing.orientation = img_in.orientation or existing.orientation
        db.commit()
        db.refresh(existing)
        return existing

    tags_obj = [get_or_create_tag(db, t) for t in img_in.tags if t.strip()]
    db_img = models.Image(
        source_id=source_id,
        file_path=img_in.file_path,
        raw_url=img_in.raw_url,
        filename=img_in.filename or img_in.file_path.split("/")[-1],
        file_size=img_in.file_size,
        mime_type=img_in.mime_type,
        width=img_in.width,
        height=img_in.height,
        orientation=img_in.orientation,
        tags=tags_obj
    )
    db.add(db_img)
    db.commit()
    db.refresh(db_img)
    return db_img

def batch_update_tags(db: Session, image_ids: List[int], add_tags: List[str], remove_tags: List[str]) -> int:
    images = db.query(models.Image).filter(models.Image.id.in_(image_ids)).all()
    add_tag_objs = [get_or_create_tag(db, t) for t in add_tags if t.strip()]
    count = 0
    for img in images:
        current_tags = set(img.tags)
        for t in add_tag_objs:
            current_tags.add(t)
        if remove_tags:
            current_tags = {t for t in current_tags if t.name not in remove_tags}
        img.tags = list(current_tags)
        count += 1
    db.commit()
    return count

def delete_image(db: Session, image_id: int) -> bool:
    db_img = get_image(db, image_id)
    if db_img:
        db.delete(db_img)
        db.commit()
        return True
    return False


# ==================== ApiKey CRUD ====================
def generate_api_key() -> str:
    return f"ak_live_{secrets.token_hex(16)}"

def get_api_key_by_key(db: Session, key: str) -> Optional[models.ApiKey]:
    return db.query(models.ApiKey).filter(models.ApiKey.key == key, models.ApiKey.is_active == True).first()

def get_api_keys(db: Session, owner_id: Optional[int] = None) -> List[models.ApiKey]:
    query = db.query(models.ApiKey)
    if owner_id:
        query = query.filter(models.ApiKey.owner_id == owner_id)
    return query.order_by(desc(models.ApiKey.id)).all()

def create_api_key(db: Session, key_in: schemas.ApiKeyCreate, owner_id: int) -> models.ApiKey:
    db_key = models.ApiKey(
        key=generate_api_key(),
        name=key_in.name,
        owner_id=owner_id,
        allowed_tags_and=json.dumps(key_in.allowed_tags_and, ensure_ascii=False),
        allowed_tags_or=json.dumps(key_in.allowed_tags_or, ensure_ascii=False),
        blocked_tags=json.dumps(key_in.blocked_tags, ensure_ascii=False),
        orientation_filter=key_in.orientation_filter,
        rate_limit_qpm=key_in.rate_limit_qpm,
        daily_quota=key_in.daily_quota,
        referer_whitelist=json.dumps(key_in.referer_whitelist, ensure_ascii=False),
        ip_whitelist=json.dumps(key_in.ip_whitelist, ensure_ascii=False)
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key

def update_api_key(db: Session, key_id: int, key_update: schemas.ApiKeyUpdate) -> Optional[models.ApiKey]:
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if not db_key:
        return None
    data = key_update.model_dump(exclude_unset=True)
    json_fields = ["allowed_tags_and", "allowed_tags_or", "blocked_tags", "referer_whitelist", "ip_whitelist"]
    for k, v in data.items():
        if k in json_fields:
            setattr(db_key, k, json.dumps(v, ensure_ascii=False))
        else:
            setattr(db_key, k, v)
    db.commit()
    db.refresh(db_key)
    return db_key

def delete_api_key(db: Session, key_id: int) -> bool:
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if db_key:
        db.delete(db_key)
        db.commit()
        return True
    return False


# ==================== Dashboard Stats CRUD ====================
def get_dashboard_stats(db: Session) -> dict:
    total_images = db.query(func.count(models.Image.id)).scalar() or 0
    total_sources = db.query(func.count(models.StorageSource.id)).scalar() or 0
    total_tags = db.query(func.count(models.Tag.id)).scalar() or 0
    total_api_keys = db.query(func.count(models.ApiKey.id)).scalar() or 0
    total_calls_all_time = db.query(func.sum(models.ApiKey.total_calls)).scalar() or 0
    
    top_tags = db.query(
        models.Tag.name,
        func.count(models.image_tag_association.c.image_id).label("count")
    ).join(models.image_tag_association, models.Tag.id == models.image_tag_association.c.tag_id, isouter=True)\
     .group_by(models.Tag.id)\
     .order_by(desc("count"))\
     .limit(10).all()

    recent_sources = db.query(models.StorageSource).order_by(desc(models.StorageSource.id)).limit(5).all()

    return {
        "total_images": total_images,
        "total_sources": total_sources,
        "total_tags": total_tags,
        "total_api_keys": total_api_keys,
        "total_calls_all_time": int(total_calls_all_time),
        "calls_today": 0,
        "top_tags": [{"name": t[0], "count": t[1]} for t in top_tags],
        "recent_sources": recent_sources
    }
