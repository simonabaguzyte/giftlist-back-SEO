from fastapi.testclient import TestClient
import pytest
from app.auth import ALGORITHM, SECRET_KEY
from app.database import get_db
from app.models import GiftList, GiftListItem, User
from main import app
from jose import jwt

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def cleanup_db():
    yield

    db = next(get_db())

    db.query(GiftListItem).delete()
    db.query(GiftList).delete()
    db.query(User).delete()
    db.commit()


def generate_test_token():
    login_data = {
        "username": "testuser",
        "password": "testpassword",
    }
    response = client.post("/token", data=login_data)
    return response.json()["access_token"]


def generate_gift_list():
    gift_list_data = {
        "name": "Test Gift List",
    }

    token = generate_test_token()

    response = client.post(
        "/gift-lists",
        headers={"Authorization": f"Bearer {token}"},
        json=gift_list_data,
    )
    return response.json()


def test_create_user():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    response = client.post("/users", json=user_data)
    assert response.status_code == 200

    created_user = response.json()
    assert "id" in created_user
    assert created_user["username"] == user_data["username"]
    assert created_user["email"] == user_data["email"]

    db = next(get_db())
    user_in_db = db.query(User).filter(User.id == created_user["id"]).first()
    assert user_in_db is not None
    assert user_in_db.username == user_data["username"]
    assert user_in_db.email == user_data["email"]
    assert user_in_db.hashed_password is not None
    assert user_in_db.hashed_password != user_data["password"]


def test_login_user():
    login_data = {
        "username": "testuser",
        "password": "testpassword",
    }

    response = client.post("/token", data=login_data)
    assert response.status_code == 200

    token_response = response.json()
    assert "access_token" in token_response
    assert token_response["token_type"] == "bearer"

    decoded_token = jwt.decode(token_response["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == login_data["username"]
    assert "exp" in decoded_token


def test_create_gift_list():
    gift_list_data = {
        "name": "Test Gift List",
    }

    token = generate_test_token()

    response = client.post(
        "/gift-lists",
        headers={"Authorization": f"Bearer {token}"},
        json=gift_list_data,
    )
    assert response.status_code == 200

    created_gift_list = response.json()
    assert "id" in created_gift_list
    assert "owner_id" in created_gift_list
    assert created_gift_list["name"] == gift_list_data["name"]
    assert created_gift_list["items"] == []
    assert "last_updated" in created_gift_list

    db = next(get_db())
    gift_list_in_db = db.query(GiftList).filter(GiftList.id == created_gift_list["id"]).first()
    assert gift_list_in_db is not None
    assert gift_list_in_db.name == gift_list_data["name"]
    assert gift_list_in_db.owner_id is not None
    assert gift_list_in_db.last_updated is not None


def test_read_gift_lists():
    token = generate_test_token()

    response = client.get(
        "/gift-lists",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    gift_lists = response.json()
    assert len(gift_lists) == 1

    gift_list = gift_lists[0]
    assert "id" in gift_list
    assert "owner_id" in gift_list
    assert "name" in gift_list
    assert "items" in gift_list
    assert "last_updated" in gift_list


def test_update_gift_list():
    token = generate_test_token()

    gift_list_data = {
        "name": "Updated Gift List",
    }

    response = client.patch(
        "/gift-lists/1",
        headers={"Authorization": f"Bearer {token}"},
        json=gift_list_data,
    )
    assert response.status_code == 200

    updated_gift_list = response.json()
    assert updated_gift_list["name"] == gift_list_data["name"]

    db = next(get_db())
    gift_list_in_db = db.query(GiftList).filter(GiftList.id == updated_gift_list["id"]).first()
    assert gift_list_in_db.name == gift_list_data["name"]


def test_delete_gift_list():
    token = generate_test_token()

    response = client.delete(
        "/gift-lists/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    db = next(get_db())
    gift_list_in_db = db.query(GiftList).filter(GiftList.id == 1).first()
    assert gift_list_in_db is None


def test_create_gift_list_item():
    token = generate_test_token()
    generate_gift_list()

    gift_list_item_data = {
        "name": "Test Gift List Item",
        "link": "https://example.com",
        "size": "Large",
        "color": "Red",
        "quantity": 1,
        "note": "This is a test gift list item.",
    }

    response = client.post(
        "/gift-lists/1/items",
        headers={"Authorization": f"Bearer {token}"},
        json=gift_list_item_data,
    )
    assert response.status_code == 200

    created_gift_list_item = response.json()
    assert "id" in created_gift_list_item
    assert "gift_list_id" in created_gift_list_item
    assert created_gift_list_item["name"] == gift_list_item_data["name"]
    assert created_gift_list_item["link"] == gift_list_item_data["link"]
    assert created_gift_list_item["size"] == gift_list_item_data["size"]
    assert created_gift_list_item["color"] == gift_list_item_data["color"]
    assert created_gift_list_item["quantity"] == gift_list_item_data["quantity"]
    assert created_gift_list_item["note"] == gift_list_item_data["note"]

    db = next(get_db())
    gift_list_item_in_db = db.query(GiftListItem).filter(GiftListItem.id == created_gift_list_item["id"]).first()
    assert gift_list_item_in_db is not None
    assert gift_list_item_in_db.name == gift_list_item_data["name"]
    assert gift_list_item_in_db.link == gift_list_item_data["link"]
    assert gift_list_item_in_db.size == gift_list_item_data["size"]
    assert gift_list_item_in_db.color == gift_list_item_data["color"]
    assert gift_list_item_in_db.quantity == gift_list_item_data["quantity"]
    assert gift_list_item_in_db.note == gift_list_item_data["note"]


def test_read_gift_list_items():
    token = generate_test_token()

    response = client.get(
        "/gift-lists/1/items",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    gift_list_items = response.json()
    assert len(gift_list_items) == 1

    gift_list_item = gift_list_items[0]
    assert "id" in gift_list_item
    assert "gift_list_id" in gift_list_item
    assert "name" in gift_list_item
    assert "link" in gift_list_item
    assert "size" in gift_list_item
    assert "color" in gift_list_item
    assert "quantity" in gift_list_item
    assert "note" in gift_list_item


def test_update_gift_list_item():
    token = generate_test_token()

    gift_list_item_data = {
        "name": "Updated Gift List Item",
        "link": "https://example.com",
        "size": "Large",
        "color": "Red",
        "quantity": 1,
        "note": "This is a test gift list item.",
    }

    response = client.patch(
        "/gift-lists/1/items/1",
        headers={"Authorization": f"Bearer {token}"},
        json=gift_list_item_data,
    )
    assert response.status_code == 200

    updated_gift_list_item = response.json()
    assert updated_gift_list_item["name"] == gift_list_item_data["name"]
    assert updated_gift_list_item["link"] == gift_list_item_data["link"]
    assert updated_gift_list_item["size"] == gift_list_item_data["size"]
    assert updated_gift_list_item["color"] == gift_list_item_data["color"]
    assert updated_gift_list_item["quantity"] == gift_list_item_data["quantity"]
    assert updated_gift_list_item["note"] == gift_list_item_data["note"]

    db = next(get_db())
    gift_list_item_in_db = db.query(GiftListItem).filter(GiftListItem.id == updated_gift_list_item["id"]).first()
    assert gift_list_item_in_db.name == gift_list_item_data["name"]
    assert gift_list_item_in_db.link == gift_list_item_data["link"]
    assert gift_list_item_in_db.size == gift_list_item_data["size"]
    assert gift_list_item_in_db.color == gift_list_item_data["color"]
    assert gift_list_item_in_db.quantity == gift_list_item_data["quantity"]
    assert gift_list_item_in_db.note == gift_list_item_data["note"]


def test_delete_gift_list_item():
    token = generate_test_token()

    response = client.delete(
        "/gift-lists/1/items/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    db = next(get_db())
    gift_list_item_in_db = db.query(GiftListItem).filter(GiftListItem.id == 1).first()
    assert gift_list_item_in_db is None