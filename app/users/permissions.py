from rest_framework.permissions import BasePermission

class CustomRBACPermission(BasePermission):
    """
    Кастомный класс разрешений, реализующий логику управления доступом на основе ролей (RBAC).
    Проверяет Пользователь -> Роли -> Правила доступа -> Ресурс, соответствующий HTTP-методу.
    """

    def has_permission(self, request, view):
        # 1. Проверка аутентификации
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Пропуск для суперпользователя
        if request.user.is_superuser:
            return True

        # 3. Получение требуемого ресурса из представления
        resource_name = getattr(view, 'required_resource', None)
        if not resource_name:
            # Если view не определяет ресурс, доступ блокируется по умолчанию для безопасности.
            return False

        # 4. Сопоставление HTTP метода с действием
        method_map = {
            'GET': 'can_read',
            'POST': 'can_create',
            'PUT': 'can_update',
            'PATCH': 'can_update',
            'DELETE': 'can_delete'
        }
        
        required_action = method_map.get(request.method)
        if not required_action:
            return False

        # 5. Проверка наличия у пользователя роли, разрешающей это действие с ресурсом
        # Используем обратную связь: Role.users -> user.roles
        # Мы запрашиваем роли, связанные с пользователем, которые удовлетворяют правилу доступа.
        
        filter_kwargs = {
            'permissions__resource__name': resource_name,
            f'permissions__{required_action}': True
        }

        has_permission = request.user.roles.filter(**filter_kwargs).exists()
        
        return has_permission
