# Authentication System Examples

This directory contains examples and usage demonstrations for the Multi-Tenant Authentication System.

## Files

- **test_auth_api.py** - Python script to test the authentication API
- **CURL_EXAMPLES.md** - cURL command examples for all API endpoints

## Quick Start

### Prerequisites

1. **Start the Django server**:
   ```bash
   cd app-aviladevops
   python manage.py runserver
   ```

2. **Create a test tenant** (if not already created):
   ```bash
   python manage.py create_tenant "Test Company" test@example.com --plan pro
   ```

### Using the Python Test Script

```bash
# Install requests library if needed
pip install requests

# Run the test script
python test_auth_api.py
```

The script will:
1. Login and obtain JWT tokens
2. List users, tenants, and roles
3. Check MFA status
4. View audit logs

Expected output:
```
Multi-Tenant Authentication API Test
============================================================

1. Login with credentials
============================================================
Login Response
============================================================
Status: 200
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}

✅ Login successful!
...
```

### Using cURL Examples

Open `CURL_EXAMPLES.md` for detailed cURL command examples for:
- Authentication (login, logout, token refresh)
- Tenant management
- User management
- Role and permission management
- User invitations
- Multi-factor authentication (MFA)
- Audit logs

## Common Workflows

### 1. Create a New Tenant

```bash
python manage.py create_tenant "My Company" owner@company.com --plan pro
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"owner","password":"ChangeMe123!"}'
```

### 3. Create a New User

```bash
TOKEN="<your-access-token>"

curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@company.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "New",
    "last_name": "User"
  }'
```

### 4. Invite a User

```bash
# Get role ID first
ROLE_ID=$(curl -s http://localhost:8000/api/auth/roles/ \
  -H "Authorization: Bearer $TOKEN" | jq -r '.results[0].id')

# Send invitation
curl -X POST http://localhost:8000/api/auth/invitations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"invitee@company.com\",\"role\":\"$ROLE_ID\"}"
```

### 5. Setup MFA

```bash
# Setup MFA device
curl -X POST http://localhost:8000/api/auth/mfa/setup/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Phone"}'

# Scan QR code with authenticator app

# Confirm with TOTP code
curl -X POST http://localhost:8000/api/auth/mfa/confirm/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"<device-id>","token":"123456"}'
```

## Troubleshooting

### Connection Refused

**Problem**: `Connection refused` error when trying to connect to the API.

**Solution**: Make sure the Django development server is running:
```bash
cd app-aviladevops
python manage.py runserver
```

### 401 Unauthorized

**Problem**: Receiving 401 Unauthorized responses.

**Solutions**:
1. Check your token is valid:
   ```bash
   # Login again to get a new token
   curl -X POST http://localhost:8000/api/auth/login/ ...
   ```

2. Token may have expired (default lifetime: 1 hour)
   ```bash
   # Refresh your token
   curl -X POST http://localhost:8000/api/auth/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh":"<your-refresh-token>"}'
   ```

### 403 Forbidden

**Problem**: Receiving 403 Forbidden responses.

**Solution**: You may not have the required permissions. Check:
1. Your user's roles: `GET /api/auth/users/<id>/`
2. Role permissions: `GET /api/auth/roles/<id>/`

### Token Not Working

**Problem**: Token authentication not working.

**Solutions**:
1. Make sure you're including the `Bearer` prefix:
   ```bash
   Authorization: Bearer <token>
   ```

2. Check token format (should be JWT with 3 parts separated by dots):
   ```
   eyJhbGci....<header>.<payload>.<signature>
   ```

### Tenant Not Found

**Problem**: Getting tenant-related errors.

**Solution**: Verify tenant exists:
```bash
python manage.py shell -c "from apps.users.models import Tenant; print(Tenant.objects.all())"
```

Create tenant if needed:
```bash
python manage.py create_tenant "Company Name" owner@company.com
```

## Testing Different Scenarios

### Test Multi-Tenant Isolation

1. Create two tenants:
   ```bash
   python manage.py create_tenant "Company A" admin@company-a.com
   python manage.py create_tenant "Company B" admin@company-b.com
   ```

2. Login as Company A admin
3. Try to access Company B resources (should fail with 403)

### Test RBAC

1. Create a user with limited role (e.g., "Viewer")
2. Login as that user
3. Try to create resources (should fail with 403)
4. Try to read resources (should succeed)

### Test MFA

1. Setup MFA for a user
2. Logout
3. Try to login (will require MFA code)
4. Use backup code if TOTP fails

### Test User Invitation

1. Send invitation to new email
2. Check email for invitation link
3. Accept invitation with new password
4. Login with new credentials

## API Response Examples

### Successful Login
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "username": "owner",
    "email": "owner@company.com",
    "tenant": {
      "id": "uuid",
      "name": "My Company",
      "domain": "my-company.aviladevops.com.br"
    },
    "roles": [...]
  }
}
```

### User List
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "username": "john.doe",
      "email": "john@company.com",
      "full_name": "John Doe",
      "tenant": "tenant-uuid",
      "roles": [...],
      "is_active": true,
      "is_verified": true
    }
  ]
}
```

### Role with Permissions
```json
{
  "id": "uuid",
  "name": "Admin",
  "description": "Full access",
  "is_system": true,
  "permissions": [
    {
      "id": "uuid",
      "resource": "user",
      "action": "create"
    },
    {
      "id": "uuid",
      "resource": "user",
      "action": "read"
    }
  ]
}
```

## Advanced Usage

### Batch Operations

Create multiple users:
```bash
for user in user1 user2 user3; do
  curl -X POST http://localhost:8000/api/auth/users/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$user\",\"email\":\"$user@company.com\",\"password\":\"Pass123!\",\"password_confirm\":\"Pass123!\"}"
done
```

### Filtering and Pagination

```bash
# Get page 2 with 10 items
curl "http://localhost:8000/api/auth/users/?page=2&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# Filter audit logs by event
curl "http://localhost:8000/api/auth/audit-logs/?event=login" \
  -H "Authorization: Bearer $TOKEN"

# Filter by date
curl "http://localhost:8000/api/auth/audit-logs/?created_at__gte=2024-01-01" \
  -H "Authorization: Bearer $TOKEN"
```

## Next Steps

- Read the [API Documentation](../docs/AUTH_API.md) for complete endpoint reference
- Check the [Setup Guide](../docs/AUTH_SETUP.md) for deployment instructions
- Review the [README](../docs/AUTH_README.md) for system overview

## Support

For issues or questions:
- GitHub Issues: https://github.com/aviladevs/SaaS/issues
- Documentation: https://docs.aviladevops.com.br
