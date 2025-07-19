from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Tag Schemas
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

# Image Schemas
class ImageBase(BaseModel):
    url: str
    description: Optional[str] = None

class ImageCreate(ImageBase):
    tags: List[str] = []

class ImageBulkCreate(BaseModel):
    urls: List[str]
    tags: List[str] = []

class ImageUpdate(BaseModel):
    filename: str

class Image(ImageBase):
    id: int
    created_at: datetime
    filename: Optional[str] = None
    filetype: Optional[str] = None
    owner_id: int
    tags: List[Tag] = []

    class Config:
        from_attributes = True

# ApiKey Schemas
class ApiKeyBase(BaseModel):
    name: str

class ApiKeyCreate(ApiKeyBase):
    tags_and: List[str] = []
    tags_or: List[str] = []

class ApiKey(ApiKeyBase):
    id: int
    key: str
    created_at: datetime
    owner_id: int
    tags_and: List[Tag] = []
    tags_or: List[Tag] = []

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True