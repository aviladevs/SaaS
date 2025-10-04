# Multi-Tenant Authentication API - cURL Examples

## Setup
```bash
# Base URL
BASE_URL="http://localhost:8000"

# Credentials
USERNAME="test"
PASSWORD="ChangeMe123!"
```

## 1. Login and Get JWT Token

```bash
# Login
curl -X POST $BASE_URL/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}"

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}

# Save token
TOKEN="<your-access-token-here>"
```

## 2. List Tenants

```bash
curl -X GET $BASE_URL/api/auth/tenants/ \
  -H "Authorization: Bearer $TOKEN"
```

## 3. Get Tenant Details

```bash
TENANT_ID="<tenant-uuid>"

curl -X GET $BASE_URL/api/auth/tenants/$TENANT_ID/ \
  -H "Authorization: Bearer $TOKEN"
```

## 4. Get Tenant Statistics

```bash
curl -X GET $BASE_URL/api/auth/tenants/$TENANT_ID/stats/ \
  -H "Authorization: Bearer $TOKEN"
```

## 5. List Users

```bash
curl -X GET $BASE_URL/api/auth/users/ \
  -H "Authorization: Bearer $TOKEN"
```

## 6. Create New User

```bash
curl -X POST $BASE_URL/api/auth/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "New",
    "last_name": "User",
    "tenant": "<tenant-uuid>",
    "role_ids": ["<role-uuid>"]
  }'
```

## 7. Activate/Deactivate User

```bash
USER_ID="<user-uuid>"

# Activate
curl -X POST $BASE_URL/api/auth/users/$USER_ID/activate/ \
  -H "Authorization: Bearer $TOKEN"

# Deactivate
curl -X POST $BASE_URL/api/auth/users/$USER_ID/deactivate/ \
  -H "Authorization: Bearer $TOKEN"
```

## 8. Assign Roles to User

```bash
curl -X POST $BASE_URL/api/auth/users/$USER_ID/assign_roles/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_ids": ["<role-uuid-1>", "<role-uuid-2>"]
  }'
```

## 9. List Roles

```bash
curl -X GET $BASE_URL/api/auth/roles/ \
  -H "Authorization: Bearer $TOKEN"
```

## 10. Create Role

```bash
curl -X POST $BASE_URL/api/auth/roles/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Manager",
    "description": "Manage projects and team",
    "permission_ids": ["<perm-uuid-1>", "<perm-uuid-2>"]
  }'
```

## 11. List Permissions

```bash
curl -X GET $BASE_URL/api/auth/permissions/ \
  -H "Authorization: Bearer $TOKEN"
```

## 12. Send User Invitation

```bash
curl -X POST $BASE_URL/api/auth/invitations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invitee@example.com",
    "role": "<role-uuid>"
  }'
```

## 13. Accept Invitation (Public endpoint)

```bash
curl -X POST $BASE_URL/api/auth/invitations/accept/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "<invitation-token>",
    "password": "NewPassword123!"
  }'
```

## 14. Resend Invitation

```bash
INVITATION_ID="<invitation-uuid>"

curl -X POST $BASE_URL/api/auth/invitations/$INVITATION_ID/resend/ \
  -H "Authorization: Bearer $TOKEN"
```

## 15. Setup MFA

```bash
# Step 1: Setup
curl -X POST $BASE_URL/api/auth/mfa/setup/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Phone"
  }'

# Response includes QR code URI and secret
{
  "device_id": "<device-uuid>",
  "secret": "JBSWY3DPEHPK3PXP",
  "uri": "otpauth://totp/..."
}

# Step 2: Scan QR code with authenticator app

# Step 3: Confirm with TOTP code
DEVICE_ID="<device-uuid>"
TOTP_CODE="123456"

curl -X POST $BASE_URL/api/auth/mfa/confirm/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"$DEVICE_ID\",
    \"token\": \"$TOTP_CODE\"
  }"

# Response includes backup codes
{
  "status": "MFA enabled",
  "backup_codes": [
    "A1B2C3D4E5F6",
    "G7H8I9J0K1L2",
    ...
  ]
}
```

## 16. Verify MFA Token

```bash
curl -X POST $BASE_URL/api/auth/mfa/verify/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456"
  }'
```

## 17. Check MFA Status

```bash
curl -X GET $BASE_URL/api/auth/mfa/status/ \
  -H "Authorization: Bearer $TOKEN"
```

## 18. Disable MFA

```bash
curl -X POST $BASE_URL/api/auth/mfa/disable/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"password\": \"$PASSWORD\"
  }"
```

## 19. List Audit Logs

```bash
# All logs
curl -X GET $BASE_URL/api/auth/audit-logs/ \
  -H "Authorization: Bearer $TOKEN"

# Filter by event
curl -X GET "$BASE_URL/api/auth/audit-logs/?event=login" \
  -H "Authorization: Bearer $TOKEN"

# Filter by user
curl -X GET "$BASE_URL/api/auth/audit-logs/?user_id=<user-uuid>" \
  -H "Authorization: Bearer $TOKEN"
```

## 20. Refresh JWT Token

```bash
REFRESH_TOKEN="<your-refresh-token>"

curl -X POST $BASE_URL/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}"

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 21. Logout

```bash
curl -X POST $BASE_URL/api/auth/logout/ \
  -H "Authorization: Bearer $TOKEN"
```

## Error Handling

All endpoints return standard HTTP status codes:

```bash
# 200 OK - Success
# 201 Created - Resource created
# 400 Bad Request - Invalid data
# 401 Unauthorized - Authentication required
# 403 Forbidden - Insufficient permissions
# 404 Not Found - Resource not found
# 500 Internal Server Error
```

Error response format:
```json
{
  "error": "Error message",
  "detail": "Detailed information"
}
```

## Tips

1. **Save your token**: Store the access token in a variable for easier use
   ```bash
   TOKEN=$(curl -X POST ... | jq -r '.access')
   ```

2. **Pretty print JSON**: Use `jq` for better formatting
   ```bash
   curl ... | jq '.'
   ```

3. **Check response headers**: Use `-v` flag
   ```bash
   curl -v ...
   ```

4. **Save response to file**:
   ```bash
   curl ... > response.json
   ```

5. **Debug with verbose output**:
   ```bash
   curl -v -X POST ... 2>&1 | less
   ```
