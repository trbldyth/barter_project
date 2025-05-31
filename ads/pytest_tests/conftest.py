import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from .factories import UserFactory, AdminFactory, AdFactory
from ..models import Condition, Category


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory():
    def factory(**kwargs):
        return UserFactory(**kwargs)
    return factory


@pytest.fixture
def authenticated_client(api_client, user_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client):
    admin = AdminFactory()
    api_client.force_authenticate(user=admin)
    return api_client


@pytest.fixture
def condition():
    condition, _ = Condition.objects.get_or_create(title="New",
                                                   defaults={"slug": "new"})
    return condition


@pytest.fixture
def category():
    category, _ = Category.objects.get_or_create(title="stuff",
                                                 defaults={"slug": "stuff"})
    return category


@pytest.fixture
def temp_image():
    from io import BytesIO
    from PIL import Image

    image = Image.new('RGB', (100, 100), color='red')
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)

    return SimpleUploadedFile(
        name='test_image.png',
        content=image_io.getvalue(),
        content_type='image/png'
    )


@pytest.fixture
def ad_fixture():
    return AdFactory
