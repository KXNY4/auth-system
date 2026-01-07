from rest_framework import generics, status, views, viewsets, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, 
    RoleSerializer, PermissionRuleSerializer
)
from .models import Role, PermissionRule, Resource
from .permissions import CustomRBACPermission

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

# --- Mock Business Logic ---

class MockOrdersView(views.APIView):
    permission_classes = (IsAuthenticated, CustomRBACPermission)
    required_resource = 'orders'

    @extend_schema(responses={200: dict})
    def get(self, request):
        return Response([
            {"id": 1, "item": "Laptop", "price": 1200},
            {"id": 2, "item": "Mouse", "price": 20}
        ])

    @extend_schema(request=dict, responses={201: dict})
    def post(self, request):
        return Response({"id": 3, "status": "created"}, status=status.HTTP_201_CREATED)

class MockReportsView(views.APIView):
    permission_classes = (IsAuthenticated, CustomRBACPermission)
    required_resource = 'reports'

    def get(self, request):
        return Response({"report_id": 101, "summary": "Sales up 20%"})
