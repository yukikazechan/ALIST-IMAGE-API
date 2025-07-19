from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas
import random
import uuid
from urllib.parse import unquote
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def delete_user_by_id(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    if user_update.username:
        db_user.username = user_update.username
    
    if user_update.password:
        db_user.hashed_password = pwd_context.hash(user_update.password)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_tag_by_name(db: Session, name: str):
    return db.query(models.Tag).filter(models.Tag.name == name).first()

def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def create_image(db: Session, image: schemas.ImageCreate, user_id: int):
    filename = unquote(os.path.basename(image.url))
    filetype = os.path.splitext(filename)[1]
    db_image = models.Image(
        url=image.url,
        description=image.description,
        filename=filename,
        filetype=filetype,
        owner_id=user_id
    )
    
    for tag_name in image.tags:
        db_tag = get_tag_by_name(db, name=tag_name)
        if db_tag is None:
            db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
        db_image.tags.append(db_tag)
        
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def create_bulk_images(db: Session, bulk_data: schemas.ImageBulkCreate, user_id: int):
    created_images = []
    for url in bulk_data.urls:
        # Skip if image with this URL already exists
        existing_image = db.query(models.Image).filter(models.Image.url == url).first()
        if existing_image:
            continue

        filename = unquote(os.path.basename(url))
        filetype = os.path.splitext(filename)[1]
        db_image = models.Image(url=url, filename=filename, filetype=filetype, owner_id=user_id)
        for tag_name in bulk_data.tags:
            db_tag = get_tag_by_name(db, name=tag_name)
            if db_tag is None:
                db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
            db_image.tags.append(db_tag)
        
        db.add(db_image)
        created_images.append(db_image)
    
    db.commit()
    for img in created_images:
        db.refresh(img)
    return created_images

def get_images(db: Session, user_id: int, skip: int = 0, limit: int = 10, tags: list[str] | None = None, sort_by: str = 'created_at', sort_order: str = 'desc', filename_like: str | None = None):
    query = db.query(models.Image).filter(models.Image.owner_id == user_id)

    if tags:
        for tag_name in tags:
            query = query.filter(models.Image.tags.any(name=tag_name))
    
    if filename_like:
        query = query.filter(models.Image.filename.ilike(f"%{filename_like}%"))

    sort_column = getattr(models.Image, sort_by, models.Image.created_at)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    total = query.count()
    images = query.offset(skip).limit(limit).all()
    return {"total": total, "images": images}

def delete_image(db: Session, image_id: int, user_id: int):
    db_image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == user_id).first()
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image

def delete_images_bulk(db: Session, image_ids: list[int], user_id: int):
    db.query(models.Image).filter(models.Image.id.in_(image_ids), models.Image.owner_id == user_id).delete(synchronize_session=False)
    db.commit()
    return {"status": "success", "deleted_ids": image_ids}

def update_image_tags(db: Session, image_id: int, tags: list[str], user_id: int):
    db_image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == user_id).first()
    if not db_image:
        return None

    # Clear existing tags
    db_image.tags.clear()

    # Add new tags
    for tag_name in tags:
        db_tag = get_tag_by_name(db, name=tag_name)
        if db_tag is None:
            db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
        db_image.tags.append(db_tag)
    
    db.commit()
    db.refresh(db_image)
    return db_image

def add_tags_to_images_bulk(db: Session, image_ids: list[int], tags: list[str], user_id: int):
    images = db.query(models.Image).filter(models.Image.id.in_(image_ids), models.Image.owner_id == user_id).all()
    if not images:
        return None

    for image in images:
        for tag_name in tags:
            db_tag = get_tag_by_name(db, name=tag_name)
            if db_tag is None:
                db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
            if db_tag not in image.tags:
                image.tags.append(db_tag)
    
    db.commit()
    return images

def update_image_filename(db: Session, image_id: int, filename: str, user_id: int):
    db_image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.owner_id == user_id).first()
    if not db_image:
        return None
    
    db_image.filename = filename
    db.commit()
    db.refresh(db_image)
    return db_image

def get_random_image(db: Session, tag_name: str | None = None):
    query = db.query(models.Image)
    if tag_name:
        query = query.join(models.Image.tags).filter(models.Tag.name == tag_name)
    
    images = query.all()
    if not images:
        return None
    
    return random.choice(images)

def get_api_key_by_key(db: Session, key: str):
    return db.query(models.ApiKey).filter(models.ApiKey.key == key).first()

def get_api_keys(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ApiKey).filter(models.ApiKey.owner_id == user_id).offset(skip).limit(limit).all()

def create_api_key(db: Session, api_key: schemas.ApiKeyCreate, user_id: int):
    db_api_key = models.ApiKey(
        key=str(uuid.uuid4()),
        name=api_key.name,
        owner_id=user_id
    )
    
    for tag_name in api_key.tags_and:
        db_tag = get_tag_by_name(db, name=tag_name)
        if db_tag is None:
            db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
        db_api_key.tags_and.append(db_tag)

    for tag_name in api_key.tags_or:
        db_tag = get_tag_by_name(db, name=tag_name)
        if db_tag is None:
            db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
        db_api_key.tags_or.append(db_tag)
        
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def delete_api_key(db: Session, api_key_id: int, user_id: int):
    db_api_key = db.query(models.ApiKey).filter(models.ApiKey.id == api_key_id, models.ApiKey.owner_id == user_id).first()
    if db_api_key:
        db.delete(db_api_key)
        db.commit()
    return db_api_key

def get_random_image_by_api_key(db: Session, key: str):
    api_key = get_api_key_by_key(db, key=key)
    if not api_key:
        return None
    
    tags_and = {tag.name for tag in api_key.tags_and}
    tags_or = {tag.name for tag in api_key.tags_or}

    if not tags_and and not tags_or:
        return get_random_image(db)

    query = db.query(models.Image)

    if tags_and:
        for tag_name in tags_and:
            query = query.filter(models.Image.tags.any(name=tag_name))
    
    if tags_or:
        query = query.filter(or_(*[models.Image.tags.any(name=tag_name) for tag_name in tags_or]))

    images = query.distinct().all()
    if not images:
        return None
        
    return random.choice(images)