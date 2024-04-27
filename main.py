"""Main file for the FastAPI application."""
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware

from app import crud, schemas, models
from app.database import SessionLocal, engine, get_db
from app import auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(db: SessionLocal, username: str, password: str):
    """Authenticate a user."""
    user = crud.get_user_by_username(db=db, username=username)
    if not user:
        return False

    if not auth.verify_password(password, user.hashed_password):
        return False

    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)):
    """Get the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc

    user = crud.get_user_by_username(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


@app.post("/users", response_model=schemas.User, tags=["auth"])
def create_user(user: schemas.UserCreate, db: SessionLocal = Depends(get_db)):
    """Register a new user."""
    return crud.create_user(db=db, user=user)


@app.post("/token", response_model=schemas.Token, tags=["auth"])
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: SessionLocal = Depends(get_db),
):
    """Get access token."""
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/gift-lists", response_model=schemas.GiftList, tags=["gift-lists"])
def create_gift_list(
    gift_list: schemas.GiftListCreate,
    current_user: schemas.User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Create a new gift list."""
    return crud.create_gift_list(db=db, gift_list=gift_list, owner_id=current_user.id)


@app.get("/gift-lists", response_model=list[schemas.GiftList], tags=["gift-lists"])
def read_gift_lists(
    current_user: schemas.User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Get user's gift lists."""
    return crud.get_user_gift_lists(db=db, user_id=current_user.id)


@app.patch("/gift-lists/{gift_list_id}", response_model=schemas.GiftList, tags=["gift-lists"])
def update_gift_list(
    gift_list_id: int,
    gift_list: schemas.GiftListUpdate,
    current_user: schemas.User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Update an existing gift list."""
    return crud.update_gift_list(db=db, gift_list_id=gift_list_id, gift_list=gift_list)


@app.delete("/gift-lists/{gift_list_id}", tags=["gift-lists"])
def delete_gift_list(
    gift_list_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Delete a gift list."""
    return crud.delete_gift_list(db=db, gift_list_id=gift_list_id)


@app.post(
    "/gift-lists/{gift_list_id}/items",
    response_model=schemas.GiftListItem,
    tags=["gift-list-items"],
)
def create_gift_list_item(
    gift_list_id: int,
    gift_list_item: schemas.GiftListItemCreate,
    current_user: schemas.User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Create a new gift list item."""
    return crud.create_gift_list_item(
        db=db,
        gift_list_item=gift_list_item,
        gift_list_id=gift_list_id,
    )


@app.get(
    "/gift-lists/{gift_list_id}/items",
    response_model=list[schemas.GiftListItem],
    tags=["gift-list-items"],
)
def read_gift_list_items(
    gift_list_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Get all items in a gift list."""
    return crud.get_gift_list_items(db=db, gift_list_id=gift_list_id)


@app.patch(
    "/gift-lists/{gift_list_id}/items/{gift_list_item_id}",
    response_model=schemas.GiftListItem,
    tags=["gift-list-items"],
)
def update_gift_list_item(
    gift_list_id: int,
    gift_list_item_id: int,
    gift_list_item: schemas.GiftListItemUpdate,
    current_user: schemas.User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Update an existing gift list item."""
    return crud.update_gift_list_item(
        db=db,
        gift_list_item_id=gift_list_item_id,
        gift_list_item=gift_list_item,
    )


@app.delete("/gift-lists/{gift_list_id}/items/{gift_list_item_id}", tags=["gift-list-items"])
def delete_gift_list_item(
    gift_list_id: int,
    gift_list_item_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db),
):
    """Delete a gift list item."""
    return crud.delete_gift_list_item(db=db, gift_list_item_id=gift_list_item_id)
