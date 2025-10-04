#!/usr/bin/env python3
"""
Example script to test the multi-tenant authentication API
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TENANT_DOMAIN = "test-company.aviladevops.com.br"

# Credentials
USERNAME = "test"
PASSWORD = "ChangeMe123!"


def print_response(response, title="Response"):
    """Pretty print API response"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def main():
    print("Multi-Tenant Authentication API Test")
    print("=" * 60)
    
    # 1. Login and get JWT token
    print("\n1. Login with credentials")
    login_url = f"{BASE_URL}/api/auth/login/"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(login_url, json=login_data)
    print_response(response, "Login Response")
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return
    
    tokens = response.json()
    access_token = tokens.get('access')
    
    print("\n✅ Login successful!")
    print(f"Access Token: {access_token[:50]}...")
    
    # Set authorization header for subsequent requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Get current user info
    print("\n2. Get current user information")
    user_url = f"{BASE_URL}/api/auth/users/"
    response = requests.get(user_url, headers=headers)
    print_response(response, "Users List")
    
    # 3. List tenants
    print("\n3. List tenants")
    tenants_url = f"{BASE_URL}/api/auth/tenants/"
    response = requests.get(tenants_url, headers=headers)
    print_response(response, "Tenants List")
    
    # 4. List roles
    print("\n4. List roles")
    roles_url = f"{BASE_URL}/api/auth/roles/"
    response = requests.get(roles_url, headers=headers)
    print_response(response, "Roles List")
    
    # 5. Get tenant statistics
    if response.status_code == 200:
        roles_data = response.json()
        if roles_data.get('results'):
            print("\n5. Get permissions for Admin role")
            # Get first role
            admin_role = None
            for role in roles_data['results']:
                if role['name'] == 'Admin':
                    admin_role = role
                    break
            
            if admin_role:
                print(f"\nAdmin Role ID: {admin_role['id']}")
                print(f"Permissions Count: {len(admin_role.get('permissions', []))}")
                print("\nSample Permissions:")
                for perm in admin_role.get('permissions', [])[:5]:
                    print(f"  - {perm['resource']}.{perm['action']}")
    
    # 6. Check MFA status
    print("\n6. Check MFA status")
    mfa_status_url = f"{BASE_URL}/api/auth/mfa/status/"
    response = requests.get(mfa_status_url, headers=headers)
    print_response(response, "MFA Status")
    
    # 7. List audit logs
    print("\n7. List recent audit logs")
    audit_url = f"{BASE_URL}/api/auth/audit-logs/"
    response = requests.get(audit_url, headers=headers)
    print_response(response, "Audit Logs")
    
    print("\n" + "=" * 60)
    print("✅ API Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
