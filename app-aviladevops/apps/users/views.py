"""
Views para o sistema de autenticação multi-tenant
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.contrib.auth import authenticate
from django.db.models import Q
import pyotp

from apps.users.models import (
    User, Tenant, Role, Permission,
    OAuthProvider, TOTPDevice, BackupCode,
    UserInvitation, AuditLog
)
from apps.users.serializers import (
    UserSerializer, UserCreateSerializer,
    TenantSerializer, RoleSerializer, PermissionSerializer,
    OAuthProviderSerializer, TOTPDeviceSerializer,
    BackupCodeSerializer, UserInvitationSerializer,
    AuditLogSerializer
)
from apps.users.permissions import (
    IsTenantMember, HasTenantPermission, IsTenantOwner
)


class TenantViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de Tenants"""
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        elif user.tenant:
            return Tenant.objects.filter(id=user.tenant.id)
        return Tenant.objects.none()
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Retorna estatísticas do tenant"""
        tenant = self.get_object()
        
        return Response({
            'user_count': tenant.get_user_count(),
            'max_users': tenant.max_users,
            'storage_limit': tenant.storage_limit,
            'plan': tenant.plan,
            'status': tenant.status,
            'roles_count': tenant.roles.count(),
            'oauth_providers_count': tenant.oauth_providers.filter(enabled=True).count(),
        })


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de Roles"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Role.objects.all()
        elif user.tenant:
            return Role.objects.filter(tenant=user.tenant)
        return Role.objects.none()
    
    def perform_create(self, serializer):
        # Definir tenant automaticamente
        if not self.request.user.is_superuser:
            serializer.save(tenant=self.request.user.tenant)
        else:
            serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """Impedir exclusão de roles do sistema"""
        role = self.get_object()
        if role.is_system:
            return Response(
                {"error": "Roles do sistema não podem ser excluídas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class PermissionViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de Permissions"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Permission.objects.all()
        elif user.tenant:
            return Permission.objects.filter(role__tenant=user.tenant)
        return Permission.objects.none()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de Users"""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        elif user.tenant:
            return User.objects.filter(tenant=user.tenant)
        return User.objects.none()
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Ativar usuário"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        # Log de auditoria
        AuditLog.objects.create(
            tenant=user.tenant,
            user=request.user,
            event='user_updated',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={'action': 'activate', 'target_user': user.username}
        )
        
        return Response({'status': 'user activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desativar usuário"""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        # Log de auditoria
        AuditLog.objects.create(
            tenant=user.tenant,
            user=request.user,
            event='user_updated',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={'action': 'deactivate', 'target_user': user.username}
        )
        
        return Response({'status': 'user deactivated'})
    
    @action(detail=True, methods=['post'])
    def assign_roles(self, request, pk=None):
        """Atribuir roles ao usuário"""
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        
        roles = Role.objects.filter(id__in=role_ids, tenant=user.tenant)
        user.roles.set(roles)
        
        # Log de auditoria
        AuditLog.objects.create(
            tenant=user.tenant,
            user=request.user,
            event='role_assigned',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={'target_user': user.username, 'roles': list(roles.values_list('name', flat=True))}
        )
        
        return Response({'status': 'roles assigned', 'roles': RoleSerializer(roles, many=True).data})


class OAuthProviderViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de OAuth Providers"""
    queryset = OAuthProvider.objects.all()
    serializer_class = OAuthProviderSerializer
    permission_classes = [IsAuthenticated, IsTenantOwner]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return OAuthProvider.objects.all()
        elif user.tenant:
            return OAuthProvider.objects.filter(tenant=user.tenant)
        return OAuthProvider.objects.none()


class UserInvitationViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de User Invitations"""
    queryset = UserInvitation.objects.all()
    serializer_class = UserInvitationSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return UserInvitation.objects.all()
        elif user.tenant:
            return UserInvitation.objects.filter(tenant=user.tenant)
        return UserInvitation.objects.none()
    
    def perform_create(self, serializer):
        # Definir tenant e invited_by automaticamente
        serializer.save(
            tenant=self.request.user.tenant,
            invited_by=self.request.user
        )
        
        # Log de auditoria
        AuditLog.objects.create(
            tenant=self.request.user.tenant,
            user=self.request.user,
            event='invitation_sent',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            details={'email': serializer.validated_data['email']}
        )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def accept(self, request):
        """Aceitar convite"""
        token = request.data.get('token')
        password = request.data.get('password')
        
        try:
            invitation = UserInvitation.objects.get(token=token, status='pending')
        except UserInvitation.DoesNotExist:
            return Response(
                {"error": "Convite inválido ou já utilizado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se convite expirou
        if invitation.expires_at < timezone.now():
            invitation.status = 'expired'
            invitation.save()
            return Response(
                {"error": "Convite expirado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Criar usuário
        username = invitation.email.split('@')[0]
        user = User.objects.create_user(
            username=username,
            email=invitation.email,
            password=password,
            tenant=invitation.tenant,
            is_verified=True
        )
        user.roles.add(invitation.role)
        
        # Atualizar convite
        invitation.status = 'accepted'
        invitation.accepted_at = timezone.now()
        invitation.save()
        
        # Log de auditoria
        AuditLog.objects.create(
            tenant=invitation.tenant,
            user=user,
            event='invitation_accepted',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={'invitation_id': str(invitation.id)}
        )
        
        return Response({
            'status': 'invitation accepted',
            'user': UserSerializer(user).data
        })
    
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Reenviar convite"""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response(
                {"error": "Apenas convites pendentes podem ser reenviados"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Estender prazo de expiração
        from datetime import timedelta
        invitation.expires_at = timezone.now() + timedelta(days=7)
        invitation.save()
        
        # Aqui você enviaria o email novamente
        # send_invitation_email(invitation)
        
        return Response({'status': 'invitation resent'})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consulta de Audit Logs"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_queryset(self):
        user = self.request.user
        queryset = AuditLog.objects.all()
        
        if not user.is_superuser:
            if user.tenant:
                queryset = queryset.filter(tenant=user.tenant)
            else:
                return AuditLog.objects.none()
        
        # Filtros opcionais
        event = self.request.query_params.get('event', None)
        user_id = self.request.query_params.get('user_id', None)
        
        if event:
            queryset = queryset.filter(event=event)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset


class MFAViewSet(viewsets.ViewSet):
    """ViewSet para gerenciamento de MFA (TOTP)"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def setup(self, request):
        """Configurar dispositivo TOTP"""
        user = request.user
        device_name = request.data.get('name', 'Default Device')
        
        # Gerar segredo TOTP
        secret = pyotp.random_base32()
        
        # Criar dispositivo não confirmado
        device = TOTPDevice.objects.create(
            user=user,
            name=device_name,
            secret=secret,
            confirmed=False
        )
        
        # Gerar URI para QR code
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='Ávila DevOps SaaS'
        )
        
        return Response({
            'device_id': device.id,
            'secret': secret,
            'uri': uri
        })
    
    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """Confirmar dispositivo TOTP com código"""
        device_id = request.data.get('device_id')
        token = request.data.get('token')
        
        try:
            device = TOTPDevice.objects.get(id=device_id, user=request.user, confirmed=False)
        except TOTPDevice.DoesNotExist:
            return Response(
                {"error": "Dispositivo não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar token
        totp = pyotp.TOTP(device.secret)
        if totp.verify(token):
            device.confirmed = True
            device.save()
            
            # Gerar códigos de backup
            backup_codes = []
            for _ in range(10):
                code = BackupCode.generate_code()
                BackupCode.objects.create(user=request.user, code=code)
                backup_codes.append(code)
            
            # Log de auditoria
            AuditLog.objects.create(
                tenant=request.user.tenant,
                user=request.user,
                event='mfa_enabled',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response({
                'status': 'MFA enabled',
                'backup_codes': backup_codes
            })
        else:
            return Response(
                {"error": "Token inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verificar token TOTP"""
        token = request.data.get('token')
        
        # Verificar em dispositivos TOTP
        devices = TOTPDevice.objects.filter(user=request.user, confirmed=True)
        for device in devices:
            totp = pyotp.TOTP(device.secret)
            if totp.verify(token):
                device.last_used_at = timezone.now()
                device.save()
                return Response({'status': 'token valid'})
        
        # Verificar códigos de backup
        try:
            backup_code = BackupCode.objects.get(
                user=request.user,
                code=token.upper(),
                used=False
            )
            backup_code.used = True
            backup_code.used_at = timezone.now()
            backup_code.save()
            return Response({'status': 'backup code valid'})
        except BackupCode.DoesNotExist:
            pass
        
        return Response(
            {"error": "Token inválido"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def disable(self, request):
        """Desabilitar MFA"""
        password = request.data.get('password')
        
        # Verificar senha
        user = authenticate(username=request.user.username, password=password)
        if not user:
            return Response(
                {"error": "Senha inválida"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remover dispositivos e códigos de backup
        TOTPDevice.objects.filter(user=request.user).delete()
        BackupCode.objects.filter(user=request.user).delete()
        
        # Log de auditoria
        AuditLog.objects.create(
            tenant=request.user.tenant,
            user=request.user,
            event='mfa_disabled',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'status': 'MFA disabled'})
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Status do MFA do usuário"""
        has_totp = TOTPDevice.objects.filter(user=request.user, confirmed=True).exists()
        backup_codes_count = BackupCode.objects.filter(user=request.user, used=False).count()
        
        return Response({
            'mfa_enabled': has_totp,
            'backup_codes_remaining': backup_codes_count
        })
