from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role, Resource, PermissionRule
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает начальные данные для тестирования (Роли, Ресурсы, Пользователи)'

    def handle(self, *args, **options):
        self.stdout.write('Запуск инициализации данных...')

        # 1. Создание ресурсов
        resources = ['orders', 'reports']
        created_resources = {}
        for res_name in resources:
            res, created = Resource.objects.get_or_create(name=res_name)
            created_resources[res_name] = res
            if created:
                self.stdout.write(f'Ресурс создан: {res_name}')
            else:
                self.stdout.write(f'Ресурс уже существует: {res_name}')

        # 2. Создание роли Менеджер
        manager_role, created = Role.objects.get_or_create(name='Manager')
        if created:
            self.stdout.write('Роль создана: Manager')
        else:
             self.stdout.write('Роль уже существует: Manager')

        # 3. Назначение прав (Manager -> orders: read, create)
        orders_res = created_resources['orders']
        rule, created = PermissionRule.objects.get_or_create(role=manager_role, resource=orders_res)
        if created:
            self.stdout.write('Правило создано для Manager -> orders')
        
        # Обновляем права
        rule.can_read = True
        rule.can_create = True
        # Убедимся, что остальные права False (хотя default False)
        rule.can_update = False
        rule.can_delete = False
        rule.save()
        self.stdout.write('Права обновлены: Manager может читать и создавать orders')

        # 4. Создание суперпользователя (если нужен)
        admin_email = 'admin@example.com'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email, 
                password='adminpass', 
                first_name='Admin', 
                last_name='Super',
                middle_name='Rootovich'
            )
            self.stdout.write(f'Суперпользователь создан: {admin_email} / adminpass')
        
        # 5. Создание тестового пользователя (Менеджер)
        manager_email = 'manager@example.com'
        if not User.objects.filter(email=manager_email).exists():
            user = User.objects.create_user(
                email=manager_email, 
                password='managerpass', 
                first_name='Ivan', 
                last_name='Managerov',
                middle_name='Ivanovich'
            )
            user.roles.add(manager_role)
            self.stdout.write(f'Пользователь создан: {manager_email} / managerpass (Role: Manager)')
        else:
            self.stdout.write(f'Пользователь уже существует: {manager_email}')

        self.stdout.write(self.style.SUCCESS('Инициализация данных завершена успешно!'))
