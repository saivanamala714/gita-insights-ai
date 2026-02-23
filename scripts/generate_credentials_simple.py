#!/usr/bin/env python3
"""
Simple admin credentials generator (no bcrypt dependency issues).
Generates API key and password hash for admin access.
"""
import secrets
import hashlib

def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)

def generate_password():
    """Generate a secure random password."""
    return secrets.token_urlsafe(16)

def hash_password_simple(password):
    """Hash password using SHA-256 (simple alternative)."""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("=" * 60)
    print("Admin Credentials Generator (Simple)")
    print("=" * 60)
    
    # Generate API key
    api_key = generate_api_key()
    
    # Generate password
    password = generate_password()
    password_hash = hash_password_simple(password)
    
    print(f"\n✅ Credentials Generated Successfully!")
    print("\n" + "=" * 60)
    print("Add these to your .env file:")
    print("=" * 60)
    print(f"\nADMIN_API_KEY={api_key}")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print(f"ADMIN_USERNAME=admin")
    print(f"\n# Your admin password (save this!):")
    print(f"# {password}")
    print("\n" + "=" * 60)
    print("IMPORTANT: Save the password above!")
    print("You'll need it to login to the admin dashboard.")
    print("=" * 60)

if __name__ == "__main__":
    main()
