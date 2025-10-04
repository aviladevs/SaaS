"""
Admin configuration for multi-tenant authentication models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.users.models import (
    User, Tenant, Role, Permission,
    OAuthProvider, TOTPDevice, BackupCode,
    UserInvitation, AuditLog
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'plan', 'status', 'owner_email', 'created_at']
    list_filter = ['plan', 'status', 'created_at']
    search_fields = ['name', 'domain', 'owner_email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'name', 'slug', 'domain', 'owner_email')
        }),
        ('Plan & Limits', {
            'fields': ('plan', 'status', 'max_users', 'storage_limit', 'trial_ends_at')
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'is_system', 'created_at']
    list_filter = ['tenant', 'is_system', 'created_at']
    search_fields = ['name', 'description', 'tenant__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_system:
            return self.readonly_fields + ['is_system']
        return self.readonly_fields


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'resource', 'action', 'created_at']
    list_filter = ['resource', 'action', 'role__tenant', 'created_at']
    search_fields = ['role__name', 'resource', 'action']
    readonly_fields = ['id', 'created_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'tenant', 'is_active', 'is_staff', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'is_verified', 'tenant', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'company']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login', 'date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'bio')}),
        (_('Company'), {'fields': ('company', 'position', 'tenant')}),
        (_('Roles'), {'fields': ('roles',)}),
        (_('Address'), {
            'fields': ('address', 'city', 'state', 'zip_code', 'country'),
            'classes': ('collapse',)
        }),
        (_('Social'), {
            'fields': ('website', 'linkedin', 'github', 'avatar'),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')
        }),
        (_('Preferences'), {
            'fields': ('language', 'timezone', 'newsletter_subscribed', 'marketing_emails'),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    filter_horizontal = ('groups', 'user_permissions', 'roles')


@admin.register(OAuthProvider)
class OAuthProviderAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'provider', 'enabled', 'auto_create_users', 'created_at']
    list_filter = ['provider', 'enabled', 'auto_create_users', 'tenant', 'created_at']
    search_fields = ['tenant__name', 'provider', 'client_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'tenant', 'provider', 'enabled')
        }),
        ('OAuth Credentials', {
            'fields': ('client_id', 'client_secret'),
            'classes': ('collapse',)
        }),
        ('SAML', {
            'fields': ('saml_metadata_url',),
            'classes': ('collapse',)
        }),
        ('User Creation', {
            'fields': ('auto_create_users', 'default_role')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TOTPDevice)
class TOTPDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'confirmed', 'created_at', 'last_used_at']
    list_filter = ['confirmed', 'created_at']
    search_fields = ['user__username', 'user__email', 'name']
    readonly_fields = ['id', 'secret', 'created_at', 'last_used_at']


@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'used', 'used_at', 'created_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__username', 'user__email', 'code']
    readonly_fields = ['id', 'code', 'used_at', 'created_at']


@admin.register(UserInvitation)
class UserInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'tenant', 'status', 'invited_by', 'created_at', 'expires_at']
    list_filter = ['status', 'tenant', 'created_at']
    search_fields = ['email', 'tenant__name', 'invited_by__username']
    readonly_fields = ['id', 'token', 'created_at', 'accepted_at']
    
    fieldsets = (
        ('Invitation Info', {
            'fields': ('id', 'tenant', 'email', 'invited_by', 'role')
        }),
        ('Status', {
            'fields': ('status', 'token', 'created_at', 'expires_at', 'accepted_at')
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'tenant', 'ip_address', 'created_at']
    list_filter = ['event', 'tenant', 'created_at']
    search_fields = ['user__username', 'user__email', 'tenant__name', 'ip_address']
    readonly_fields = ['id', 'tenant', 'user', 'event', 'ip_address', 'user_agent', 'details', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
