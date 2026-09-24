from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional, Dict, Any

# ==================== Tag Schemas ====================
class TagBase(BaseModel):
    name: str
    slug: Optional[str] = None
    color: Optional[str] = "#3b82f6"

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    image_count: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Storage Source Schemas ====================
class StorageSourceBase(BaseModel):
    name: str
    base_url: str
    root_path: str = "/"
    token: Optional[str] = None
    auto_sync_interval: int = 0

class StorageSourceCreate(StorageSourceBase):
    pass

class StorageSourceUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    root_path: Optional[str] = None
    token: Optional[str] = None
    auto_sync_interval: Optional[int] = None

class StorageSourceResponse(StorageSourceBase):
    id: int
    last_sync_at: Optional[datetime] = None
    sync_status: str = "idle"
    sync_message: Optional[str] = None
    total_images_indexed: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Image Schemas ====================
class ImageBase(BaseModel):
    raw_url: str
    file_path: str
    filename: str
    file_size: int = 0
    mime_type: str = "image/jpeg"
    width: int = 0
    height: int = 0
    orientation: str = "landscape"
    blurhash: Optional[str] = None
    dominant_color: Optional[str] = None
    is_active: bool = True

class ImageCreate(BaseModel):
    raw_url: str
    file_path: str
    filename: Optional[str] = None
    file_size: int = 0
    mime_type: str = "image/jpeg"
    width: int = 0
    height: int = 0
    orientation: str = "landscape"
    tags: List[str] = []

class ImageUpdate(BaseModel):
    filename: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None

class ImageBatchTagRequest(BaseModel):
    image_ids: List[int]
    add_tags: List[str] = []
    remove_tags: List[str] = []

class ImageResponse(ImageBase):
    id: int
    source_id: Optional[int] = None
    view_count: int = 0
    created_at: Optional[datetime] = None
    tags: List[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)

class RandomImageMetadata(BaseModel):
    id: int
    url: str
    filename: str
    width: int
    height: int
    orientation: str
    mime_type: str
    file_size: int
    dominant_color: Optional[str] = None
    blurhash: Optional[str] = None
    tags: List[str] = []


# ==================== API Key Schemas ====================
class ApiKeyBase(BaseModel):
    name: str
    allowed_tags_and: List[str] = []
    allowed_tags_or: List[str] = []
    blocked_tags: List[str] = []
    orientation_filter: str = "all"
    rate_limit_qpm: int = 120
    daily_quota: int = -1
    referer_whitelist: List[str] = []
    ip_whitelist: List[str] = []

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKeyUpdate(BaseModel):
    name: Optional[str] = None
    allowed_tags_and: Optional[List[str]] = None
    allowed_tags_or: Optional[List[str]] = None
    blocked_tags: Optional[List[str]] = None
    orientation_filter: Optional[str] = None
    rate_limit_qpm: Optional[int] = None
    daily_quota: Optional[int] = None
    referer_whitelist: Optional[List[str]] = None
    ip_whitelist: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ApiKeyResponse(BaseModel):
    id: int
    key: str
    name: str
    allowed_tags_and: List[str] = []
    allowed_tags_or: List[str] = []
    blocked_tags: List[str] = []
    orientation_filter: str = "all"
    rate_limit_qpm: int = 120
    daily_quota: int = -1
    referer_whitelist: List[str] = []
    ip_whitelist: List[str] = []
    total_calls: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== User & Auth Schemas ====================
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== Dashboard & Stats Schemas ====================
class DashboardStats(BaseModel):
    total_images: int = 0
    total_sources: int = 0
    total_tags: int = 0
    total_api_keys: int = 0
    total_calls_all_time: int = 0
    calls_today: int = 0
    top_tags: List[Dict[str, Any]] = []
    recent_sources: List[StorageSourceResponse] = []
