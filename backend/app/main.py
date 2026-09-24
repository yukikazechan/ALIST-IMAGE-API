from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, SessionLocal
from . import crud, schemas
from .services.random_pool import random_pool
from .routers import auth_router, random_api, admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Initialize default admin if not exists
    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_username(db, settings.DEFAULT_ADMIN_USER)
        if not admin_user:
            crud.create_user(
                db=db,
                user=schemas.UserCreate(
                    username=settings.DEFAULT_ADMIN_USER,
                    password=settings.DEFAULT_ADMIN_PASS
                ),
                is_admin=True
            )
        # Pre-warm in-memory random pool
        random_pool.reload_from_db(db)
    finally:
        db.close()
        
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(admin_router.router, prefix=settings.API_V1_STR)
app.include_router(random_api.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "indexed_images": len(random_pool.all_ids)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
