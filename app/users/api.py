from rest_framework import generics, status, views, viewsets, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, 
    RoleSerializer, PermissionRuleSerializer,
    OrderSerializer, ReportSerializer
)
from .models import Role, PermissionRule, Resource, Order, Report
from .permissions import CustomRBACPermission
from . import services

User = get_user_model()

# --- Auth ---

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

class LogoutView(views.APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(request={'refresh': str}, responses={205: None})
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Обновление профиля пользователя."""
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Мягкое удаление учетной записи пользователя."""
        user = request.user
        user.soft_delete()
        # В идеале нужно занести текущий токен в черный список.
        # В задании сказано "токен аннулируется".
        # Можно занести refresh токен в черный список, если он передан,
        # но access токен работает без состояния (кроме времени жизни).
        # Но так как user.is_active становится False, последующие запросы не пройдут проверку.
        return Response({"detail": "Аккаунт удален."}, status=status.HTTP_204_NO_CONTENT)

# --- RBAC Admin ---

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsAdminUser,)

class PermissionRuleViewSet(viewsets.ModelViewSet):
    queryset = PermissionRule.objects.all()
    serializer_class = PermissionRuleSerializer
    permission_classes = (IsAdminUser,)

# --- Бизнес-логика (Реальные модели + Сервисный слой) ---

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, CustomRBACPermission)
    required_resource = 'orders'

    def get_queryset(self):
        return services.get_user_orders(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = services.create_order(request.user, serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED, headers=headers)

class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = (IsAuthenticated, CustomRBACPermission)
    required_resource = 'reports'

    def get_queryset(self):
        return services.get_user_reports(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = services.create_report(request.user, serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED, headers=headers)
