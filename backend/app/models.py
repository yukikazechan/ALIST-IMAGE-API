from sqlalchemy import (
    Column, Integer, String, Text, BigInteger, Boolean, DateTime,
    ForeignKey, Table, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Many-to-Many Association: Images <-> Tags
image_tag_association = Table(
    'image_tag_association',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id', ondelete="CASCADE"), primary_key=True, index=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True, index=True)
)

class StorageSource(Base):
    __tablename__ = "storage_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    base_url = Column(String(255), nullable=False) # e.g. http://127.0.0.1:5244
    root_path = Column(String(255), nullable=False, default="/") # e.g. /Wallpapers
    token = Column(String(255), nullable=True) # AList API Token
    auto_sync_interval = Column(Integer, default=0) # in minutes, 0 = disabled
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_status = Column(String(32), default="idle") # idle, syncing, error
    sync_message = Column(Text, nullable=True)
    total_images_indexed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    images = relationship("Image", back_populates="source", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, index=True, nullable=False)
    slug = Column(String(64), unique=True, index=True, nullable=True)
    color = Column(String(16), default="#3b82f6") # Hex color for UI badge
    image_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    images = relationship("Image", secondary=image_tag_association, back_populates="tags")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("storage_sources.id", ondelete="SET NULL"), nullable=True, index=True)
    file_path = Column(String(512), unique=True, index=True, nullable=False)
    raw_url = Column(Text, nullable=False)
    filename = Column(String(255), index=True, nullable=False)
    file_size = Column(BigInteger, default=0)
    mime_type = Column(String(64), default="image/jpeg")
    
    # Image Metrics
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    orientation = Column(String(16), default="landscape", index=True) # landscape, portrait, square
    blurhash = Column(String(64), nullable=True)
    dominant_color = Column(String(16), nullable=True) # e.g. #2D3748
    
    # Stats & Flags
    view_count = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    source = relationship("StorageSource", back_populates="images")
    tags = relationship("Tag", secondary=image_tag_association, back_populates="images")
    owner = relationship("User", back_populates="images")

    __table_args__ = (
        Index('idx_images_active_orient', 'is_active', 'orientation'),
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(64), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Filter rules (stored as JSON arrays / strings)
    allowed_tags_and = Column(Text, default="[]") # JSON list of tag names that MUST all match
    allowed_tags_or = Column(Text, default="[]")  # JSON list of tag names (any match)
    blocked_tags = Column(Text, default="[]")     # JSON list of tag names to exclude
    orientation_filter = Column(String(16), default="all") # all, landscape, portrait, square
    
    # Rate Limits & Security
    rate_limit_qpm = Column(Integer, default=120) # requests per minute
    daily_quota = Column(Integer, default=-1) # -1 = unlimited
    referer_whitelist = Column(Text, default="[]") # JSON list of allowed referers
    ip_whitelist = Column(Text, default="[]")      # JSON list of allowed client IPs
    
    # Stats
    total_calls = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="api_keys")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    images = relationship("Image", back_populates="owner")
    api_keys = relationship("ApiKey", back_populates="owner", cascade="all, delete-orphan")


class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="SET NULL"), nullable=True, index=True)
    client_ip = Column(String(64), nullable=True)
    referer = Column(String(255), nullable=True)
    status_code = Column(Integer, default=200)
    latency_ms = Column(Integer, default=0)
    mode = Column(String(16), default="redirect") # redirect, proxy, json
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
