import pytest
from .factories import UserFactory

@pytest.mark.django_db
def test_user_creation():
    user = UserFactory()
    assert user.id is not None
    assert user.is_active is True

@pytest.mark.django_db
def test_user_signup(api_client):
    url = "/api/v1/users/signup/"
    data = {
        "username": "testuser",
        "password": "securepassword123",
        "password_verify": "securepassword123",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201

@pytest.mark.django_db
def test_user_signup_invalid_password_verify(api_client):
    url = "/api/v1/users/signup/"
    data = {
        "username": "testuser",
        "password": "securepassword123",
        "password_verify": "securepassword1234",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_user_login(api_client, user_factory):
    user = user_factory(password="testpass123")
    url = "/api/v1/users/login/"
    data = {
        "username": user.username,
        "password": "testpass123",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 200
