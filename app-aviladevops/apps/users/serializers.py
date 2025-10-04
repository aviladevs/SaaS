"""
Serializers para o sistema de autenticação multi-tenant
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import timedelta
from apps.users.models import (
    User, Tenant, Role, Permission, 
    OAuthProvider, TOTPDevice, BackupCode,
    UserInvitation, AuditLog
)


class TenantSerializer(serializers.ModelSerializer):
    """Serializer para Tenant"""
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'domain', 'plan', 'status',
            'max_users', 'storage_limit', 'owner_email',
            'created_at', 'updated_at', 'trial_ends_at',
            'settings', 'user_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_count']
    
    def get_user_count(self, obj):
        return obj.get_user_count()


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer para Permission"""
    
    class Meta:
        model = Permission
        fields = ['id', 'resource', 'action', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer para Role"""
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = [
            'id', 'tenant', 'name', 'description', 'is_system',
            'permissions', 'permission_ids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system']
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids, role__tenant=role.tenant)
            role.permissions.set(permissions)
        
        return role
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids, role__tenant=instance.tenant)
            instance.permissions.set(permissions)
        
        return instance


class UserSerializer(serializers.ModelSerializer):
    """Serializer para User"""
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'company', 'position', 'bio', 'avatar',
            'address', 'city', 'state', 'zip_code', 'country',
            'website', 'linkedin', 'github',
            'is_verified', 'is_active', 'is_staff',
            'tenant', 'roles', 'role_ids',
            'language', 'timezone',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'full_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de usuário"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'company', 'position',
            'tenant', 'role_ids'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        role_ids = validated_data.pop('role_ids', [])
        
        user = User.objects.create_user(**validated_data)
        
        if role_ids:
            roles = Role.objects.filter(id__in=role_ids, tenant=user.tenant)
            user.roles.set(roles)
        
        return user


class OAuthProviderSerializer(serializers.ModelSerializer):
    """Serializer para OAuthProvider"""
    
    class Meta:
        model = OAuthProvider
        fields = [
            'id', 'tenant', 'provider', 'client_id', 'client_secret',
            'saml_metadata_url', 'enabled', 'auto_create_users',
            'default_role', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'client_secret': {'write_only': True}
        }


class TOTPDeviceSerializer(serializers.ModelSerializer):
    """Serializer para TOTPDevice"""
    
    class Meta:
        model = TOTPDevice
        fields = ['id', 'user', 'name', 'confirmed', 'created_at', 'last_used_at']
        read_only_fields = ['id', 'user', 'secret', 'created_at', 'last_used_at']


class BackupCodeSerializer(serializers.ModelSerializer):
    """Serializer para BackupCode"""
    
    class Meta:
        model = BackupCode
        fields = ['id', 'code', 'used', 'used_at', 'created_at']
        read_only_fields = ['id', 'code', 'used', 'used_at', 'created_at']


class UserInvitationSerializer(serializers.ModelSerializer):
    """Serializer para UserInvitation"""
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = UserInvitation
        fields = [
            'id', 'tenant', 'email', 'invited_by', 'invited_by_name',
            'role', 'role_name', 'status',
            'created_at', 'expires_at', 'accepted_at'
        ]
        read_only_fields = ['id', 'token', 'status', 'created_at', 'accepted_at']
    
    def create(self, validated_data):
        # Gerar token e data de expiração
        validated_data['token'] = UserInvitation.generate_token()
        validated_data['expires_at'] = timezone.now() + timedelta(days=7)
        
        invitation = UserInvitation.objects.create(**validated_data)
        
        # Aqui você poderia enviar email de convite
        # send_invitation_email(invitation)
        
        return invitation


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para AuditLog"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'tenant', 'tenant_name', 'user', 'user_name',
            'event', 'ip_address', 'user_agent', 'details',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
