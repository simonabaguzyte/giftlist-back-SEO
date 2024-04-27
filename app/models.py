"""Models for the application."""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    gift_lists = relationship("GiftList", back_populates="owner")


class GiftList(Base):
    """GiftList model."""

    __tablename__ = "gift-lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="gift_lists")

    items = relationship("GiftListItem", back_populates="gift_list")

    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class GiftListItem(Base):
    """GiftListItem model."""

    __tablename__ = "gift-list-items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    link = Column(String, nullable=True)
    size = Column(String, nullable=True)
    color = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    note = Column(String, nullable=True)

    gift_list_id = Column(Integer, ForeignKey("gift-lists.id"))
    gift_list = relationship("GiftList", back_populates="items")
