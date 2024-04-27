"""CRUD operations for the database."""
from sqlalchemy.orm import Session

from app import models, schemas
from app import auth


def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user."""
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_username(db: Session, username: str):
    """Get a user by email."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    """Get a user by ID."""
    return db.query(models.User).get(user_id)


def create_gift_list(db: Session, gift_list: schemas.GiftListCreate, owner_id: int):
    """Create a new gift list."""
    db_gift_list = models.GiftList(name=gift_list.name, owner_id=owner_id)

    db.add(db_gift_list)
    db.commit()
    db.refresh(db_gift_list)

    return db_gift_list


def get_user_gift_lists(db: Session, user_id: int):
    """Get all gift lists for a user."""
    user = get_user_by_id(db=db, user_id=user_id)
    return user.gift_lists


def get_gift_list_by_id(db: Session, gift_list_id: int):
    """Get a gift list by ID."""
    return db.query(models.GiftList).get(gift_list_id)


def update_gift_list(db: Session, gift_list_id: int, gift_list: schemas.GiftListUpdate):
    """Update a gift list."""
    db_gift_list = get_gift_list_by_id(db=db, gift_list_id=gift_list_id)

    db_gift_list.name = gift_list.name
    db.commit()
    db.refresh(db_gift_list)

    return db_gift_list


def delete_gift_list(db: Session, gift_list_id: int):
    """Delete a gift list."""
    db_gift_list = get_gift_list_by_id(db=db, gift_list_id=gift_list_id)

    db.delete(db_gift_list)
    db.commit()


def create_gift_list_item(
    db: Session,
    gift_list_item: schemas.GiftListItemCreate,
    gift_list_id: int,
):
    """Create a new gift list item."""
    db_gift_list_item = models.GiftListItem(
        **gift_list_item.model_dump(),
        gift_list_id=gift_list_id,
    )

    db.add(db_gift_list_item)
    db.commit()
    db.refresh(db_gift_list_item)

    return db_gift_list_item


def get_gift_list_items(db: Session, gift_list_id: int):
    """Get all gift list items for a gift list."""
    gift_list = get_gift_list_by_id(db=db, gift_list_id=gift_list_id)
    return gift_list.items


def get_gift_list_item_by_id(db: Session, gift_list_item_id: int):
    """Get a gift list item by ID."""
    return db.query(models.GiftListItem).get(gift_list_item_id)


def update_gift_list_item(
    db: Session,
    gift_list_item_id: int,
    gift_list_item: schemas.GiftListItemUpdate,
):
    """Update a gift list item."""
    db_gift_list_item = get_gift_list_item_by_id(db=db, gift_list_item_id=gift_list_item_id)

    for field, value in gift_list_item.model_dump(exclude_unset=True).items():
        setattr(db_gift_list_item, field, value)

    db.commit()
    db.refresh(db_gift_list_item)

    return db_gift_list_item


def delete_gift_list_item(db: Session, gift_list_item_id: int):
    """Delete a gift list item."""
    db_gift_list_item = get_gift_list_item_by_id(db=db, gift_list_item_id=gift_list_item_id)

    db.delete(db_gift_list_item)
    db.commit()
