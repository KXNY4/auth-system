from django.db import transaction
from .models import Order, Report

def get_user_orders(user):
    """
    Получить список заказов, доступных пользователю.
    """
    # Если пользователь суперюзер или имеет глобальные права - можно менять логику.
    # Пока возвращаем только свои.
    return Order.objects.filter(owner=user)

@transaction.atomic
def create_order(user, data):
    """
    Создание заказа для пользователя.
    """
    order = Order.objects.create(owner=user, **data)
    return order

def get_user_reports(user):
    """
    Получение отчетов.
    """
    return Report.objects.filter(author=user)

@transaction.atomic
def create_report(user, data):
    """
    Создание отчета.
    """
    report = Report.objects.create(author=user, **data)
    return report
