from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name

class Resource(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")  # например, "orders" (заказы), "reports" (отчеты)

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"

    def __str__(self):
        return self.name

class PermissionRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions', verbose_name="Роль")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name="Ресурс")
    can_create = models.BooleanField(default=False, verbose_name="Может создавать")
    can_read = models.BooleanField(default=False, verbose_name="Может читать")
    can_update = models.BooleanField(default=False, verbose_name="Может обновлять")
    can_delete = models.BooleanField(default=False, verbose_name="Может удалять")

    class Meta:
        unique_together = ('role', 'resource')
        verbose_name = "Правило доступа"
        verbose_name_plural = "Правила доступа"
    
    def __str__(self):
        return f"{self.role} -> {self.resource}"

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Поле Email должно быть заполнено'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email адрес'), unique=True)
    first_name = models.CharField(_('Имя'), max_length=150)
    last_name = models.CharField(_('Фамилия'), max_length=150)
    middle_name = models.CharField(_('Отчество'), max_length=150, blank=True)
    is_active = models.BooleanField(_('Активен'), default=True)
    is_staff = models.BooleanField(_('Персонал'), default=False)
    
    # Кастомные роли RBAC
    roles = models.ManyToManyField(Role, related_name='users', blank=True, verbose_name="Роли")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def soft_delete(self):
        """Мягкое удаление пользователя."""
        self.is_active = False
        self.save()

class Order(models.Model):
    item = models.CharField(max_length=255, verbose_name="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Владелец", null=True, blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    
    def __str__(self):
        return f"Order #{self.id} - {self.item}"

class Report(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name="Автор", null=True, blank=True)

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"

    def __str__(self):
        return self.title
