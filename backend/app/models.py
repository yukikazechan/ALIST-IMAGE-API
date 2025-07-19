from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

ImageTagAssociation = Table(
    'image_tag_association', Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    filetype = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="images")
    tags = relationship("Tag", secondary=ImageTagAssociation, back_populates="images")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    images = relationship("Image", secondary=ImageTagAssociation, back_populates="tags")

ApiKeyTagAssociationAnd = Table(
    'api_key_tag_association_and', Base.metadata,
    Column('api_key_id', Integer, ForeignKey('api_keys.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

ApiKeyTagAssociationOr = Table(
    'api_key_tag_association_or', Base.metadata,
    Column('api_key_id', Integer, ForeignKey('api_keys.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="api_keys")
    tags_and = relationship("Tag", secondary=ApiKeyTagAssociationAnd)
    tags_or = relationship("Tag", secondary=ApiKeyTagAssociationOr)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    images = relationship("Image", back_populates="owner")
    api_keys = relationship("ApiKey", back_populates="owner")