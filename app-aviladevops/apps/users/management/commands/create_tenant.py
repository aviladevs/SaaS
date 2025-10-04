"""
Django management command to create a new tenant with default roles and permissions
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.users.models import Tenant, Role, Permission
from django.utils.text import slugify

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a new tenant with default roles and permissions'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Tenant name')
        parser.add_argument('owner_email', type=str, help='Owner email address')
        parser.add_argument(
            '--domain',
            type=str,
            help='Custom domain (default: slug.aviladevops.com.br)'
        )
        parser.add_argument(
            '--plan',
            type=str,
            default='basic',
            choices=['basic', 'pro', 'enterprise'],
            help='Subscription plan'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='ChangeMe123!',
            help='Owner password (default: ChangeMe123!)'
        )

    def handle(self, *args, **options):
        name = options['name']
        owner_email = options['owner_email']
        plan = options['plan']
        password = options['password']
        
        # Generate slug from name
        slug = slugify(name)
        
        # Generate domain
        domain = options.get('domain') or f"{slug}.aviladevops.com.br"
        
        # Check if tenant already exists
        if Tenant.objects.filter(slug=slug).exists():
            raise CommandError(f'Tenant with slug "{slug}" already exists')
        
        if Tenant.objects.filter(domain=domain).exists():
            raise CommandError(f'Tenant with domain "{domain}" already exists')
        
        self.stdout.write(self.style.SUCCESS(f'Creating tenant: {name}'))
        
        # Create tenant
        tenant = Tenant.objects.create(
            name=name,
            slug=slug,
            domain=domain,
            owner_email=owner_email,
            plan=plan,
            status='active',
            max_users=10 if plan == 'basic' else 100 if plan == 'pro' else -1,
            storage_limit=10 if plan == 'basic' else 100 if plan == 'pro' else 1000
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Tenant created: {tenant.name}'))
        self.stdout.write(f'  Domain: {tenant.domain}')
        self.stdout.write(f'  Plan: {tenant.plan}')
        
        # Create default roles
        self.stdout.write('Creating default roles...')
        
        admin_role = Role.objects.create(
            tenant=tenant,
            name='Admin',
            description='Full access to all features',
            is_system=True
        )
        
        manager_role = Role.objects.create(
            tenant=tenant,
            name='Manager',
            description='Manage team and projects',
            is_system=True
        )
        
        user_role = Role.objects.create(
            tenant=tenant,
            name='User',
            description='Standard user access',
            is_system=True
        )
        
        viewer_role = Role.objects.create(
            tenant=tenant,
            name='Viewer',
            description='Read-only access',
            is_system=True
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Roles created'))
        
        # Create permissions for admin role (full access)
        self.stdout.write('Creating permissions...')
        
        resources = ['user', 'tenant', 'service', 'project', 'blog', 'contact', 'analytics', 'settings']
        actions = ['create', 'read', 'update', 'delete', 'list', 'export']
        
        permission_count = 0
        for resource in resources:
            for action in actions:
                Permission.objects.create(
                    role=admin_role,
                    resource=resource,
                    action=action
                )
                permission_count += 1
        
        # Manager permissions (no tenant management)
        manager_resources = ['user', 'service', 'project', 'blog', 'contact']
        for resource in manager_resources:
            for action in ['create', 'read', 'update', 'delete', 'list']:
                Permission.objects.create(
                    role=manager_role,
                    resource=resource,
                    action=action
                )
                permission_count += 1
        
        # User permissions (limited)
        user_resources = ['service', 'project', 'contact']
        for resource in user_resources:
            for action in ['create', 'read', 'update', 'list']:
                Permission.objects.create(
                    role=user_role,
                    resource=resource,
                    action=action
                )
                permission_count += 1
        
        # Viewer permissions (read-only)
        for resource in resources:
            Permission.objects.create(
                role=viewer_role,
                resource=resource,
                action='read'
            )
            Permission.objects.create(
                role=viewer_role,
                resource=resource,
                action='list'
            )
            permission_count += 2
        
        self.stdout.write(self.style.SUCCESS(f'✓ {permission_count} permissions created'))
        
        # Create owner user
        self.stdout.write('Creating owner user...')
        
        username = owner_email.split('@')[0]
        
        owner = User.objects.create_user(
            username=username,
            email=owner_email,
            password=password,
            tenant=tenant,
            first_name='Owner',
            last_name=name,
            is_verified=True,
            is_active=True
        )
        owner.roles.add(admin_role)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Owner user created: {owner.username}'))
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Tenant Setup Complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Tenant: {tenant.name}')
        self.stdout.write(f'Domain: {tenant.domain}')
        self.stdout.write(f'Owner: {owner_email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write('')
        self.stdout.write('Roles created:')
        self.stdout.write(f'  - Admin ({admin_role.permissions.count()} permissions)')
        self.stdout.write(f'  - Manager ({manager_role.permissions.count()} permissions)')
        self.stdout.write(f'  - User ({user_role.permissions.count()} permissions)')
        self.stdout.write(f'  - Viewer ({viewer_role.permissions.count()} permissions)')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  Remember to:'))
        self.stdout.write('  1. Change the owner password')
        self.stdout.write('  2. Configure OAuth providers if needed')
        self.stdout.write('  3. Set up DNS for the domain')
        self.stdout.write('  4. Review tenant settings')
        self.stdout.write('')
        self.stdout.write(f'Login URL: https://{tenant.domain}/api/auth/login/')
        self.stdout.write(f'Admin URL: https://{tenant.domain}/admin/')
