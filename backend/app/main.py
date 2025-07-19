import httpx
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, models, schemas, auth
from .database import SessionLocal, engine, Base

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    user = crud.get_user_by_username(db, username="admin")
    if not user:
        user_in = schemas.UserCreate(username="admin", password="admin")
        crud.create_user(db=db, user=user_in, is_admin=True)
    db.close()

# CORS Middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Cannot register with username 'admin'")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/api/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.delete("/api/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user_to_delete = crud.get_user(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_to_delete.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete an admin user")

    return crud.delete_user_by_id(db, user_id=user_id)

@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/api/users/me", response_model=schemas.User)
def update_user_me(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Check if new username is already taken
    if user_update.username and crud.get_user_by_username(db, username=user_update.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    updated_user = crud.update_user(db, user_id=current_user.id, user_update=user_update)
    return updated_user

@app.post("/api/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not crud.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/images/", response_model=schemas.Image)
def create_image(image: schemas.ImageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_image(db=db, image=image, user_id=current_user.id)

@app.post("/api/images/bulk", response_model=List[schemas.Image])
def create_bulk_images(bulk_data: schemas.ImageBulkCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_bulk_images(db=db, bulk_data=bulk_data, user_id=current_user.id)

class PaginatedImages(schemas.BaseModel):
    total: int
    images: List[schemas.Image]

@app.get("/api/images/", response_model=PaginatedImages)
def read_images(
    skip: int = 0,
    limit: int = 10,
    tags: Optional[List[str]] = Query(None),
    sort_by: str = 'created_at',
    sort_order: str = 'desc',
    filename_like: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = crud.get_images(db, user_id=current_user.id, skip=skip, limit=limit, tags=tags, sort_by=sort_by, sort_order=sort_order, filename_like=filename_like)
    return result

@app.delete("/api/images/{image_id}", response_model=schemas.Image)
def delete_image(image_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_image = crud.delete_image(db, image_id=image_id, user_id=current_user.id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image

class BulkDeleteImages(schemas.BaseModel):
    image_ids: List[int]

@app.post("/api/images/bulk-delete")
def delete_images_bulk(data: BulkDeleteImages, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.delete_images_bulk(db, image_ids=data.image_ids, user_id=current_user.id)

class ImageUpdateTags(schemas.BaseModel):
    tags: List[str]

@app.put("/api/images/{image_id}/tags", response_model=schemas.Image)
def update_image_tags(image_id: int, tags_data: ImageUpdateTags, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_image = crud.update_image_tags(db, image_id=image_id, tags=tags_data.tags, user_id=current_user.id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image

class BulkAddTags(schemas.BaseModel):
    image_ids: List[int]
    tags: List[str]

@app.post("/api/images/bulk-add-tags", response_model=List[schemas.Image])
def add_tags_to_images_bulk(data: BulkAddTags, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    images = crud.add_tags_to_images_bulk(db, image_ids=data.image_ids, tags=data.tags, user_id=current_user.id)
    if images is None:
        raise HTTPException(status_code=404, detail="One or more images not found")
    return images

@app.put("/api/images/{image_id}/rename", response_model=schemas.Image)
def rename_image(image_id: int, image_update: schemas.ImageUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_image = crud.update_image_filename(db, image_id=image_id, filename=image_update.filename, user_id=current_user.id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image

@app.get("/api/random/")
def get_random_image_url(tag: Optional[str] = None, db: Session = Depends(get_db)):
    random_image = crud.get_random_image(db, tag_name=tag)
    if random_image is None:
        raise HTTPException(status_code=404, detail="No images found")
    return {"url": random_image.url}

@app.post("/api/keys/", response_model=schemas.ApiKey)
def create_api_key(api_key: schemas.ApiKeyCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_api_key(db=db, api_key=api_key, user_id=current_user.id)

@app.get("/api/keys/", response_model=List[schemas.ApiKey])
def read_api_keys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    api_keys = crud.get_api_keys(db, user_id=current_user.id, skip=skip, limit=limit)
    return api_keys

@app.delete("/api/keys/{api_key_id}", response_model=schemas.ApiKey)
def delete_api_key(api_key_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_api_key = crud.delete_api_key(db, api_key_id=api_key_id, user_id=current_user.id)
    if db_api_key is None:
        raise HTTPException(status_code=404, detail="API Key not found")
    return db_api_key

@app.get("/api/v1/random/{key}")
async def get_random_image_by_key(key: str, db: Session = Depends(get_db)):
    random_image = crud.get_random_image_by_api_key(db, key=key)
    if random_image is None:
        raise HTTPException(status_code=404, detail="No images found for this key")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(random_image.url, follow_redirects=True)
            resp.raise_for_status()

            # Force content type to a common image type to prevent download
            content_type = resp.headers.get("Content-Type", "image/png")
            if "application" in content_type:
                content_type = "image/png" # Fallback for incorrect server headers

            return StreamingResponse(resp.iter_bytes(), media_type=content_type)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error fetching image from source: {exc}")

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# --- Static files and SPA hosting ---
# This must be at the end of the file to ensure API routes are matched first.
import os
from fastapi.staticfiles import StaticFiles

static_files_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")

# Mount the entire frontend as a static application.
# The html=True flag enables SPA support by serving index.html for any path not found.
# This single mount handles serving index.html, /assets/*, and other static files.
# IMPORTANT: This must come AFTER all API routes are defined.
app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="spa")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 5235))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)