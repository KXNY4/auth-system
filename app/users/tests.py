import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Role, Resource, PermissionRule, Order
from .services import create_order, get_user_orders

User = get_user_model()

@pytest.fixture
def user():
    """Фикстура для создания пользователя"""
    return User.objects.create_user(email='test@example.com', password='password')

@pytest.fixture
def client():
    """Фикстура API клиента DRF"""
    return APIClient()

@pytest.fixture
def tester_role():
    """Фикстура для роли тестировщика"""
    role, _ = Role.objects.get_or_create(name='Tester')
    return role

@pytest.fixture
def orders_resource():
    """Фикстура для ресурса заказов"""
    resource, _ = Resource.objects.get_or_create(name='orders')
    return resource

@pytest.fixture
def permission_rule(tester_role, orders_resource):
    """
    Фикстура для правила доступа.
    Изначально даем права только на чтение.
    """
    return PermissionRule.objects.create(
        role=tester_role, resource=orders_resource,
        can_read=True, can_create=False
    )

@pytest.fixture
def user_with_role(user, tester_role):
    """Пользователь с назначенной ролью"""
    user.roles.add(tester_role)
    return user

@pytest.fixture
def auth_token(client, user_with_role):
    """Получение JWT токена для пользователя"""
    resp = client.post('/api/v1/auth/login/', {'email': 'test@example.com', 'password': 'password'})
    assert resp.status_code == status.HTTP_200_OK
    return resp.data['access']

class TestServices:
    @pytest.mark.django_db
    def test_create_order(self, user):
        """Тест сервиса создания заказа"""
        data = {'item': 'Test Item', 'price': 100}
        order = create_order(user, data)
        assert order.owner == user
        assert order.item == 'Test Item'

    @pytest.mark.django_db
    def test_get_user_orders(self, user):
        """Тест сервиса получения заказов пользователя"""
        create_order(user, {'item': 'Item 1', 'price': 10})
        create_order(user, {'item': 'Item 2', 'price': 20})
        orders = get_user_orders(user)
        assert orders.count() == 2

class TestAPI:
    @pytest.mark.django_db
    def test_list_orders_permission(self, client, auth_token, permission_rule):
        """Тест списка заказов (должен быть доступен, т.к. can_read=True)"""
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_token}')
        response = client.get('/api/v1/resources/orders/')
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_create_order_permission_denied(self, client, auth_token, permission_rule):
        """Тест создания заказа (должен быть запрещен, т.к. can_create=False)"""
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_token}')
        response = client.post('/api/v1/resources/orders/', {'item': 'New', 'price': 50})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_create_order_permission_allowed(self, client, auth_token, permission_rule, user):
        """Тест создания заказа после выдачи прав (должен быть разрешен)"""
        # Выдаем права на создание
        permission_rule.can_create = True
        permission_rule.save()
        
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_token}')
        response = client.post('/api/v1/resources/orders/', {'item': 'New', 'price': 50})
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1
        assert Order.objects.first().owner == user
