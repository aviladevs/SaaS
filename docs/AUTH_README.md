# Multi-Tenant Authentication System with SSO

A comprehensive authentication system for the Ávila DevOps SaaS platform featuring multi-tenancy, role-based access control (RBAC), single sign-on (SSO), and multi-factor authentication (MFA).

## Features

### 🏢 Multi-Tenant Architecture
- **Subdomain-based tenant isolation** - Each tenant gets their own subdomain (e.g., `company-a.aviladevops.com.br`)
- **Data segregation** - Complete data isolation between tenants
- **Tenant-specific configurations** - Customizable settings per tenant
- **Flexible plans** - Basic, Pro, and Enterprise tiers with different limits

### 🔐 Authentication Methods
- **JWT Tokens** - Secure token-based authentication with refresh rotation
- **OAuth 2.0 / OpenID Connect** - Support for Google, Microsoft, GitHub
- **SAML 2.0** - Enterprise SSO for corporate identity providers
- **Email/Password** - Traditional authentication with strong password policies
- **Session Authentication** - Cookie-based sessions with Redis backing

### 👥 Role-Based Access Control (RBAC)
- **Granular permissions** - Control access at resource and action level
- **Custom roles** - Create tenant-specific roles with specific permissions
- **System roles** - Pre-defined Admin, Manager, User, and Viewer roles
- **Role inheritance** - Users can have multiple roles

### 🛡️ Security Features
- **Multi-Factor Authentication (MFA)** - TOTP-based 2FA with backup codes
- **Password policies** - Configurable complexity requirements per tenant
- **Session management** - Redis-backed sessions with configurable timeouts
- **Audit logging** - Complete tracking of authentication events
- **Rate limiting** - Protection against brute force attacks
- **HTTPS enforcement** - Secure connections in production

### 👤 User Management
- **User invitations** - Email-based invitation system with expiration
- **Bulk operations** - Import/export users (planned)
- **User activation/deactivation** - Control user access
- **Profile management** - Extended user profiles with custom fields

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a tenant
python manage.py create_tenant \
  "My Company" \
  owner@mycompany.com \
  --plan pro \
  --password SecurePass123!

# Run development server
python manage.py runserver
```

### Usage

```python
# Login and get JWT token
POST /api/auth/login/
{
  "username": "owner@mycompany.com",
  "password": "SecurePass123!"
}

# Use token in subsequent requests
GET /api/auth/users/
Authorization: Bearer <access_token>
```

## Documentation

- **[API Documentation](./AUTH_API.md)** - Complete API reference
- **[Setup Guide](./AUTH_SETUP.md)** - Installation and configuration
- **[Architecture](../docs/architecture.md)** - System architecture overview

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Load Balancer                          │
│                    (Nginx + SSL/TLS)                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼────────┐
│  Tenant A      │  │  Tenant B      │
│  company-a.*   │  │  company-b.*   │
└───────┬────────┘  └───────┬────────┘
        │                   │
        └─────────┬─────────┘
                  │
    ┌─────────────▼──────────────┐
    │   Django Application       │
    │   - TenantMiddleware       │
    │   - JWT Authentication     │
    │   - RBAC Authorization     │
    │   - OAuth/SAML Support     │
    └─────────────┬──────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼────────┐
│  PostgreSQL    │  │     Redis      │
│  (Multi-tenant)│  │  (Sessions)    │
└────────────────┘  └────────────────┘
```

## Models

### Core Models

- **Tenant** - Multi-tenant isolation and configuration
- **User** - Extended Django user with tenant association
- **Role** - RBAC role definition
- **Permission** - Granular permission model
- **OAuthProvider** - OAuth/SAML provider configuration per tenant
- **TOTPDevice** - MFA device configuration
- **BackupCode** - MFA backup codes
- **UserInvitation** - User invitation system
- **AuditLog** - Authentication event logging

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login and get JWT token
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/auth/registration/` - Register new user (if enabled)

### Tenant Management
- `GET /api/auth/tenants/` - List tenants
- `POST /api/auth/tenants/` - Create tenant
- `GET /api/auth/tenants/{id}/` - Get tenant details
- `GET /api/auth/tenants/{id}/stats/` - Get tenant statistics

### User Management
- `GET /api/auth/users/` - List users
- `POST /api/auth/users/` - Create user
- `GET /api/auth/users/{id}/` - Get user details
- `POST /api/auth/users/{id}/activate/` - Activate user
- `POST /api/auth/users/{id}/deactivate/` - Deactivate user
- `POST /api/auth/users/{id}/assign_roles/` - Assign roles

### RBAC
- `GET /api/auth/roles/` - List roles
- `POST /api/auth/roles/` - Create role
- `GET /api/auth/permissions/` - List permissions

### User Invitations
- `POST /api/auth/invitations/` - Send invitation
- `POST /api/auth/invitations/accept/` - Accept invitation
- `POST /api/auth/invitations/{id}/resend/` - Resend invitation

### MFA
- `POST /api/auth/mfa/setup/` - Setup MFA device
- `POST /api/auth/mfa/confirm/` - Confirm MFA device
- `POST /api/auth/mfa/verify/` - Verify MFA token
- `POST /api/auth/mfa/disable/` - Disable MFA
- `GET /api/auth/mfa/status/` - Get MFA status

### Audit Logs
- `GET /api/auth/audit-logs/` - List audit logs
- `GET /api/auth/audit-logs/?event=login` - Filter by event
- `GET /api/auth/audit-logs/?user_id={id}` - Filter by user

## Management Commands

### Create Tenant
```bash
python manage.py create_tenant <name> <owner_email> \
  --domain <custom-domain> \
  --plan {basic|pro|enterprise} \
  --password <password>
```

Example:
```bash
python manage.py create_tenant \
  "Acme Corp" \
  admin@acmecorp.com \
  --plan enterprise \
  --password SecurePass123!
```

## Configuration

### Environment Variables

```env
# Required
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=*.aviladevops.com.br

# Database
DB_NAME=aviladevops
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

### Django Settings

Key settings in `core/settings.py`:

```python
# Custom User Model
AUTH_USER_MODEL = 'users.User'

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# Multi-tenant
TENANT_MODEL = 'users.Tenant'
MIDDLEWARE = [
    ...
    'apps.users.middleware.TenantMiddleware',
]
```

## Security Best Practices

1. **Always use HTTPS** in production
2. **Change SECRET_KEY** for production
3. **Enable MFA** for admin accounts
4. **Rotate OAuth secrets** regularly
5. **Monitor audit logs** for suspicious activity
6. **Keep dependencies updated**
7. **Use strong passwords** (enforced by policy)
8. **Configure CORS** properly
9. **Enable rate limiting** on all endpoints
10. **Regular security audits**

## Testing

Run tests:
```bash
# All tests
python manage.py test apps.users

# Specific test
python manage.py test apps.users.tests.test_authentication
```

## Performance

- **Database queries** - Optimized with select_related and prefetch_related
- **Caching** - Redis for sessions and frequently accessed data
- **Connection pooling** - PostgreSQL connection pooling
- **JWT tokens** - Stateless authentication reduces database load
- **Middleware optimization** - Efficient tenant detection

## Monitoring

- **Audit logs** - Track all authentication events
- **Error tracking** - Sentry integration for error monitoring
- **Metrics** - Prometheus-compatible metrics
- **Health checks** - Built-in health check endpoints

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is part of the Ávila DevOps SaaS platform.

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/aviladevs/SaaS/issues
- **Email**: support@aviladevops.com.br
- **Documentation**: https://docs.aviladevops.com.br

## Roadmap

- [ ] Frontend components (React/Next.js)
- [ ] Mobile SDK (React Native)
- [ ] Bulk user import/export
- [ ] Advanced audit log filtering
- [ ] Passwordless authentication
- [ ] Biometric authentication
- [ ] Session replay for security investigation
- [ ] Advanced threat detection
- [ ] Compliance reports (GDPR, SOC 2)

## Changelog

### Version 1.0.0 (Current)
- Multi-tenant architecture with subdomain isolation
- JWT authentication with token rotation
- OAuth 2.0 support (Google, Microsoft, GitHub)
- SAML 2.0 support
- RBAC with granular permissions
- MFA with TOTP and backup codes
- User invitation system
- Comprehensive audit logging
- Django admin interface
- Management commands for tenant creation
- API documentation
