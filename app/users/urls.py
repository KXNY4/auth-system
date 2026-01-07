from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, LogoutView, UserProfileView,
    RoleViewSet, PermissionRuleViewSet,
    MockOrdersView, MockReportsView
)

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'rules', PermissionRuleViewSet)

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    # Mock Resources
    path('resources/orders/', MockOrdersView.as_view(), name='orders'),
    path('resources/reports/', MockReportsView.as_view(), name='reports'),

    # Admin RBAC
    path('admin/', include(router.urls)),
]
