from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, Resource, PermissionRule, Order, Report

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    ordering = ('email',)
    list_filter = ('is_staff', 'is_active', 'roles')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'middle_name')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'roles')}),
        ('Важные даты', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password', 'roles'),
        }),
    )
    filter_horizontal = ('roles',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PermissionRule)
class PermissionRuleAdmin(admin.ModelAdmin):
    list_display = ('role', 'resource', 'can_create', 'can_read', 'can_update', 'can_delete')
    list_filter = ('role', 'resource')
    list_editable = ('can_create', 'can_read', 'can_update', 'can_delete')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'price', 'owner', 'created_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('item', 'owner__email')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'author__email')
