"""Pydantic schemas for FastAPI application."""
from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    """Base schema for User."""

    email: str
    username: str


class UserCreate(UserBase):
    """Schema for creating a User."""

    password: str


class UserLogin(UserCreate):
    """Schema for User login."""


class User(UserBase):
    """Schema for User."""

    id: int

    class Config:
        """Pydantic configuration."""

        orm_mode = True


class Token(BaseModel):
    """Schema for token."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token data."""

    username: str | None = None


class GiftListItemBase(BaseModel):
    """Base schema for GiftListItem."""

    name: str
    link: str
    size: str | None = None
    color: str | None = None
    quantity: int | None = None
    note: str | None = None


class GiftListItemCreate(GiftListItemBase):
    """Schema for creating a GiftListItem."""


class GiftListItemUpdate(GiftListItemBase):
    """Schema for updating a GiftListItem."""

    name: str | None = None
    link: str | None = None


class GiftListItem(GiftListItemBase):
    """Schema for GiftListItem."""

    id: int
    gift_list_id: int

    class Config:
        """Pydantic configuration."""

        orm_mode = True


class GiftListBase(BaseModel):
    """Base schema for GiftList."""

    name: str


class GiftListCreate(GiftListBase):
    """Schema for creating a GiftList."""


class GiftListUpdate(GiftListBase):
    """Schema for updating a GiftList."""


class GiftList(GiftListBase):
    """Schema for GiftList."""

    id: int
    owner_id: int
    items: list["GiftListItem"]
    last_updated: datetime

    class Config:
        """Pydantic configuration."""

        orm_mode = True
