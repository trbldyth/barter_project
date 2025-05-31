import pytest
from ..models import Category, Condition, ExchangeProposal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
User = get_user_model()


@pytest.mark.django_db
def test_condition_creation(admin_client):
    url = "/api/v1/conditions/"
    data = {
        "title": "excellent",
        "slug": "excellent",
    }
    response = admin_client.post(url, data, format="json")
    second_response = admin_client.post(url, data, format="json")

    assert response.status_code == 201
    assert second_response.status_code == 400


@pytest.mark.django_db
def test_condition_regular_user_creation(authenticated_client):
    url = "/api/v1/conditions/"
    data = {
        "title": "excellent",
        "slug": "excellent",
    }
    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_category_creation(admin_client):
    url = "/api/v1/categories/"
    data = {
        "title": "stuff",
        "slug": "stuff",
    }
    response = admin_client.post(url, data, format="json")
    second_response = admin_client.post(url, data, format="json")

    assert response.status_code == 201
    assert second_response.status_code == 400


@pytest.mark.django_db
def test_category_regular_user_creation(authenticated_client):
    url = "/api/v1/categories/"
    data = {
        "title": "stuff",
        "slug": "stuff",
    }
    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_advertisment_unauth_creation(api_client, condition,
                                      category, temp_image):
    url = "/api/v1/ads/"
    data = {
        "title": "test_ad",
        "description": "test_description",
        "image_url": temp_image,
        "category": [category.id,],
        "condition": condition.id
        }
    response = api_client.post(url, data, format="multipart")
    assert response.status_code == 403


@pytest.mark.django_db
def test_advertisment_creation(authenticated_client, condition,
                               category, temp_image):
    url = "/api/v1/ads/"
    data = {
        "title": "test_ad",
        "description": "test_description",
        "image_url": temp_image,
        "category": [category.id,],
        "condition": condition.id
    }
    response = authenticated_client.post(url, data, format="multipart")
    assert response.status_code == 201
    ad_url = f"/api/v1/ads/{response.data['id']}/"
    get_response = authenticated_client.get(ad_url)
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_advertisment_with_invalid_data_creation(authenticated_client,
                                                 condition, category):
    url = "/api/v1/ads/"
    data = {
        "title": "test_ad",
        "description": "test_description",
        "image_url": "",
        "category": [category.id,],
        "condition": condition.id
    }
    response = authenticated_client.post(url, data, format="multipart")
    assert response.status_code == 201
    data = {
        "title": "test_ad",
        "description": "test_description",
        "image_url": "",
        "category": [category.id,],
        "condition": ""
    }
    response = authenticated_client.post(url, data, format="multipart")
    assert response.status_code == 400
    data = {
        "title": "test_ad",
        "description": "test_description",
        "image_url": "",
        "category": [],
        "condition": condition.id
    }
    response = authenticated_client.post(url, data, format="multipart")
    assert response.status_code == 400


@pytest.mark.django_db
def test_ad_update_by_author(authenticated_client, ad_fixture, condition,
                             category, temp_image):
    ad = ad_fixture(user=authenticated_client.handler._force_user)

    url = f"/api/v1/ads/{ad.id}/"
    data = {
        "title": "New title",
        "description": "New description",
        "image_url": temp_image,
        "condition": condition.id,
        "category": category.id
    }
    response = authenticated_client.put(url, data, format="multipart")

    assert response.status_code == 200
    assert response.data["title"] == "New title"
    assert response.data['description'] == "New description"
    assert response.data["condition"] == {
        'id': condition.id, 'title': condition.title, 'slug': condition.slug}


@pytest.mark.django_db
def test_ad_update_by_another_user(authenticated_client, user_factory,
                                   ad_fixture):
    ad = ad_fixture(user=user_factory())

    url = f"/api/v1/ads/{ad.id}/"
    data = {
        "title": "Hack title",
    }
    response = authenticated_client.patch(url, data, format="multipart")

    assert response.status_code == 403


@pytest.mark.django_db
def test_ad_delete_by_author(authenticated_client, ad_fixture):
    ad = ad_fixture(user=authenticated_client.handler._force_user)

    url = f"/api/v1/ads/{ad.id}/"
    response = authenticated_client.delete(url, format="json")

    assert response.status_code == 204


@pytest.mark.django_db
def test_ad_delete_by_another_user(authenticated_client, user_factory,
                                   ad_fixture):
    ad = ad_fixture(user=user_factory())

    url = f"/api/v1/ads/{ad.id}/"
    response = authenticated_client.delete(url, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_filter_ads_by_category(api_client, ad_fixture, category):
    category1 = category
    category2, _ = Category.objects.get_or_create(
        title="electronics", defaults={"slug": "electronics"})
    ad_fixture.create_batch(2, category=[category1])
    ad_fixture(category=[category2, category1])
    ad_fixture(category=[category2])
    response = api_client.get(f"/api/v1/ads/?category__slug={category1.slug}")
    response2 = api_client.get("/api/v1/ads/?category__slug=unreal_slug")
    assert response.status_code == 200
    assert len(response.data) == 3
    assert response.status_code == 200
    assert len(response2.data) == 0


@pytest.mark.django_db
def test_filter_ads_by_condition(api_client, ad_fixture, condition):
    condition1 = condition
    condition2, _ = Condition.objects.get_or_create(title="cond",
                                                    defaults={"slug": "cond"})
    assert condition1 != condition2
    ad_fixture.create_batch(2, condition=condition2)
    ad_fixture(condition=condition1)
    response = api_client.get(
        f"/api/v1/ads/?condition__slug={condition2.slug}")
    response2 = api_client.get("/api/v1/ads/?condition__slug=unreal_slug")
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response2.status_code == 200
    assert len(response2.data) == 0


@pytest.mark.django_db
def test_search_ads_by_title_description(api_client, ad_fixture):
    ad_fixture(title="Computer", description="Brand new Computer")
    ad_fixture(title="site.com", description="Selling site")
    ad_fixture(title="Babysitter", description="New service")
    response1 = api_client.get("/api/v1/ads/?search=new")
    response4 = api_client.get("/api/v1/ads/?search=service")
    response5 = api_client.get("/api/v1/ads/?search=somesearch")
    assert response1.status_code == 200
    assert len(response1.data) == 2
    assert response4.status_code == 200
    assert len(response4.data) == 1
    assert response5.status_code == 200
    assert len(response5.data) == 0


@pytest.mark.django_db
def test_ads_pagination(api_client, ad_fixture):
    ad_fixture.create_batch(15)
    response1 = api_client.get("/api/v1/ads/?limit=3")
    response2 = api_client.get("/api/v1/ads/?limit=10&offset=10")
    assert response1.status_code == 200
    assert len(response1.data["results"]) == 3
    assert len(response2.data["results"]) == 5
    assert response1.data["previous"] is None
    assert response2.data["next"] is None
    assert response1.data["count"] == 15
    assert "api/v1/ads/?limit=3&offset=3" in response1.data["next"]
    assert "api/v1/ads/?limit=10" in response2.data["previous"]


@pytest.mark.django_db
def test_exchange_propose_create_and_list(authenticated_client, ad_fixture):
    user1 = User.objects.create_user(username='First', password='123')
    user1_client = APIClient()
    user1_client.force_authenticate(user=user1)
    assert user1_client is not None
    user2 = User.objects.create(username='Second')
    ad1 = ad_fixture.create(
        title="First", user=authenticated_client.handler._force_user)
    ad2 = ad_fixture.create(title="Second", user=user1)
    url = f"/api/v1/propose/{user1.id}/"
    data1 = {
        "ad_sender": ad1.id,
        "ad_receiver": ad2.id,
        "comment": "sss"
    }
    response = authenticated_client.post(url, data1, format="json")
    assert response.status_code == 201
    exchange = ExchangeProposal.objects.get(
        ad_sender=ad1.id, ad_receiver=ad2.id)
    assert exchange.status == "pending"
    update_url = f"/api/v1/exchanges/{exchange.id}/"
    update_data = {
        "status": "accepted"
    }
    response_update = user1_client.put(update_url, update_data, format="json")
    updated_exchange = ExchangeProposal.objects.get(
        ad_sender=ad1.id, ad_receiver=ad2.id)
    assert response_update.status_code == 201
    assert updated_exchange.status == "accepted"
    ad3 = ad_fixture.create(
        title="Third", user=authenticated_client.handler._force_user)
    data2 = {
        "ad_sender": ad3.id,
        "ad_receiver": ad2.id,
        "comment": "comment"
    }
    authenticated_client.post(url, data2, format="json")
    list_sended_url = "/api/v1/exchanges/sended/"
    list_received_url = "/api/v1/exchanges/received/"
    sended_response = authenticated_client.get(list_sended_url)
    assert sended_response.status_code == 200
    assert len(sended_response.data) == 2
    received_response = user1_client.get(list_received_url)
    assert received_response.status_code == 200
    assert len(received_response.data) == 2
    filter_by_status_url = "/api/v1/exchanges/received/?status=accepted"
    filter_by_status_response = user1_client.get(filter_by_status_url)
    assert filter_by_status_response.status_code == 200
    assert len(filter_by_status_response.data) == 1
    ad4 = ad_fixture.create(title="Fourth", user=user2)
    data3 = {
        "ad_sender": ad3.id,
        "ad_receiver": ad4.id,
        "comment": "sss"
    }
    data4 = {
        "ad_sender": ad1.id,
        "ad_receiver": ad4.id,
        "comment": "comment"
    }
    ya_url = f"/api/v1/propose/{user2.id}/"
    q = authenticated_client.post(ya_url, data3, format="json")
    assert q.status_code == 201
    filter_by_receiver_url = (f"/api/v1/exchanges/sended/"
                              f"?ad_receiver__user="
                              f"{user1_client.handler._force_user.id}")
    filter_by_receiver_response = authenticated_client.get(
        filter_by_receiver_url)
    assert filter_by_receiver_response.status_code == 200
    assert len(filter_by_receiver_response.data) == 2
    bad_response = authenticated_client.post(url, data4, format="json")
    assert bad_response.status_code == 400
    data5 = {
        "ad_sender": ad1.id,
        "ad_receiver": ad3.id,
        "comment": "comment"
    }
    propose_yourself_url = (f"/api/v1/propose/"
                            f"{authenticated_client.handler._force_user.id}/")
    propose_yourself_response = authenticated_client.post(
        propose_yourself_url, data5, format="json")
    assert propose_yourself_response.status_code == 400
