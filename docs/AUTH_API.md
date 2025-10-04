# Multi-Tenant Authentication System - API Documentation

## Overview

This document describes the multi-tenant authentication system with SSO support implemented for the Ávila DevOps SaaS platform.

## Base URL

```
http://localhost:8000/api/auth/
```

## Authentication

The API supports multiple authentication methods:

1. **JWT Tokens** - Primary authentication method
2. **Session Authentication** - For web applications
3. **OAuth 2.0 / OpenID Connect** - Google, Microsoft, GitHub
4. **SAML 2.0** - For enterprise clients

### JWT Token Authentication

Include the token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Token Endpoints

#### Obtain Token Pair
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "user",
    "tenant": {...}
  }
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Tenant Management

### List Tenants
```http
GET /api/auth/tenants/

Response:
{
  "count": 10,
  "results": [
    {
      "id": "uuid",
      "name": "Company A",
      "slug": "company-a",
      "domain": "company-a.aviladevops.com.br",
      "plan": "pro",
      "status": "active",
      "max_users": 100,
      "storage_limit": 100,
      "owner_email": "owner@company-a.com",
      "user_count": 45,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Tenant
```http
POST /api/auth/tenants/
Content-Type: application/json

{
  "name": "New Company",
  "slug": "new-company",
  "domain": "new-company.aviladevops.com.br",
  "owner_email": "owner@newcompany.com",
  "plan": "basic",
  "max_users": 10,
  "storage_limit": 10
}

Response: 201 Created
{
  "id": "uuid",
  "name": "New Company",
  ...
}
```

### Get Tenant Statistics
```http
GET /api/auth/tenants/{id}/stats/

Response:
{
  "user_count": 45,
  "max_users": 100,
  "storage_limit": 100,
  "plan": "pro",
  "status": "active",
  "roles_count": 5,
  "oauth_providers_count": 2
}
```

## User Management

### List Users
```http
GET /api/auth/users/

Response:
{
  "count": 45,
  "results": [
    {
      "id": "uuid",
      "username": "john.doe",
      "email": "john.doe@company-a.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "tenant": "uuid",
      "roles": [...],
      "is_active": true,
      "is_verified": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create User
```http
POST /api/auth/users/
Content-Type: application/json

{
  "username": "jane.smith",
  "email": "jane.smith@company-a.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "tenant": "tenant-uuid",
  "role_ids": ["role-uuid-1", "role-uuid-2"]
}

Response: 201 Created
{
  "id": "uuid",
  "username": "jane.smith",
  ...
}
```

### Activate/Deactivate User
```http
POST /api/auth/users/{id}/activate/
POST /api/auth/users/{id}/deactivate/

Response:
{
  "status": "user activated"
}
```

### Assign Roles to User
```http
POST /api/auth/users/{id}/assign_roles/
Content-Type: application/json

{
  "role_ids": ["role-uuid-1", "role-uuid-2"]
}

Response:
{
  "status": "roles assigned",
  "roles": [...]
}
```

## Role-Based Access Control (RBAC)

### List Roles
```http
GET /api/auth/roles/

Response:
{
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "tenant": "tenant-uuid",
      "name": "Admin",
      "description": "Full access to all features",
      "is_system": false,
      "permissions": [...],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Role
```http
POST /api/auth/roles/
Content-Type: application/json

{
  "name": "Project Manager",
  "description": "Manage projects and team members",
  "permission_ids": ["perm-uuid-1", "perm-uuid-2"]
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Project Manager",
  ...
}
```

### List Permissions
```http
GET /api/auth/permissions/

Response:
{
  "count": 20,
  "results": [
    {
      "id": "uuid",
      "resource": "user",
      "action": "create",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## User Invitations

### Send Invitation
```http
POST /api/auth/invitations/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "role": "role-uuid"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "newuser@example.com",
  "invited_by": "current-user-uuid",
  "role": "role-uuid",
  "status": "pending",
  "expires_at": "2024-01-08T00:00:00Z"
}
```

### Accept Invitation
```http
POST /api/auth/invitations/accept/
Content-Type: application/json

{
  "token": "invitation-token-here",
  "password": "NewPass123!"
}

Response:
{
  "status": "invitation accepted",
  "user": {...}
}
```

### Resend Invitation
```http
POST /api/auth/invitations/{id}/resend/

Response:
{
  "status": "invitation resent"
}
```

## Multi-Factor Authentication (MFA)

### Setup MFA
```http
POST /api/auth/mfa/setup/
Content-Type: application/json

{
  "name": "My Phone"
}

Response:
{
  "device_id": "uuid",
  "secret": "JBSWY3DPEHPK3PXP",
  "uri": "otpauth://totp/user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Avila+DevOps+SaaS"
}
```

### Confirm MFA Device
```http
POST /api/auth/mfa/confirm/
Content-Type: application/json

{
  "device_id": "uuid",
  "token": "123456"
}

Response:
{
  "status": "MFA enabled",
  "backup_codes": [
    "A1B2C3D4E5F6",
    "G7H8I9J0K1L2",
    ...
  ]
}
```

### Verify MFA Token
```http
POST /api/auth/mfa/verify/
Content-Type: application/json

{
  "token": "123456"
}

Response:
{
  "status": "token valid"
}
```

### Disable MFA
```http
POST /api/auth/mfa/disable/
Content-Type: application/json

{
  "password": "user-password"
}

Response:
{
  "status": "MFA disabled"
}
```

### Check MFA Status
```http
GET /api/auth/mfa/status/

Response:
{
  "mfa_enabled": true,
  "backup_codes_remaining": 8
}
```

## OAuth Providers

### List OAuth Providers
```http
GET /api/auth/oauth-providers/

Response:
{
  "count": 2,
  "results": [
    {
      "id": "uuid",
      "tenant": "tenant-uuid",
      "provider": "google",
      "enabled": true,
      "auto_create_users": true,
      "default_role": "role-uuid"
    }
  ]
}
```

### Configure OAuth Provider
```http
POST /api/auth/oauth-providers/
Content-Type: application/json

{
  "provider": "microsoft",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "enabled": true,
  "auto_create_users": true,
  "default_role": "role-uuid"
}

Response: 201 Created
{
  "id": "uuid",
  "provider": "microsoft",
  ...
}
```

## Audit Logs

### List Audit Logs
```http
GET /api/auth/audit-logs/
GET /api/auth/audit-logs/?event=login
GET /api/auth/audit-logs/?user_id=user-uuid

Response:
{
  "count": 100,
  "results": [
    {
      "id": "uuid",
      "tenant": "tenant-uuid",
      "tenant_name": "Company A",
      "user": "user-uuid",
      "user_name": "John Doe",
      "event": "login",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "details": {},
      "created_at": "2024-01-01T10:30:00Z"
    }
  ]
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "error": "Error message here",
  "detail": "Detailed error information"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 10 requests per minute per IP
- **General API endpoints**: 100 requests per minute per user
- **Bulk operations**: 10 requests per minute per user

## Permissions

The system uses a granular permission model with the following resources:

- `user` - User Management
- `tenant` - Tenant Management
- `service` - Service Management
- `project` - Project Management
- `blog` - Blog Management
- `contact` - Contact Management
- `analytics` - Analytics
- `settings` - Settings

And the following actions:

- `create` - Create new resources
- `read` - View resources
- `update` - Modify existing resources
- `delete` - Remove resources
- `list` - List multiple resources
- `export` - Export data

## Security Best Practices

1. **Always use HTTPS** in production
2. **Store JWT tokens securely** (httpOnly cookies recommended)
3. **Implement CORS properly** for your domain
4. **Enable MFA** for sensitive accounts
5. **Rotate secrets regularly** (JWT secret, OAuth secrets)
6. **Monitor audit logs** for suspicious activity
7. **Use strong passwords** (min 8 chars, complexity rules)
8. **Implement rate limiting** on all endpoints
9. **Keep dependencies updated**
10. **Regular security audits**
