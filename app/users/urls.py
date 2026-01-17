from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api import (
    RegisterView, LogoutView, UserProfileView,
    RoleViewSet, PermissionRuleViewSet,
    OrderViewSet, ReportViewSet
)

# Маршрутизатор админки
admin_router = DefaultRouter()
admin_router.register(r'roles', RoleViewSet)
admin_router.register(r'rules', PermissionRuleViewSet)

# Маршрутизатор ресурсов
resources_router = DefaultRouter()
resources_router.register(r'orders', OrderViewSet, basename='orders')
resources_router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    # Аутентификация
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    # Ресурсы (CRUD через ViewSets)
    path('resources/', include(resources_router.urls)),

    # Админка RBAC
    path('admin/', include(admin_router.urls)),
]
