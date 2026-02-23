#!/usr/bin/env python3
"""
Generate admin API key and password hash for Firestore chat history.

Usage:
    python scripts/generate_admin_key.py
    python scripts/generate_admin_key.py --password yourpassword
"""
import secrets
import argparse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def hash_password(password: str):
    """Hash a password."""
    return pwd_context.hash(password)


def main():
    parser = argparse.ArgumentParser(description='Generate admin credentials')
    parser.add_argument('--password', type=str, help='Password to hash')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Admin Credentials Generator")
    print("=" * 60)
    
    # Generate API key
    api_key = generate_api_key()
    print(f"\nADMIN_API_KEY={api_key}")
    
    # Generate password hash
    if args.password:
        password_hash = hash_password(args.password)
        print(f"\nADMIN_PASSWORD_HASH={password_hash}")
        print(f"\nPassword: {args.password}")
    else:
        # Generate a random password
        random_password = secrets.token_urlsafe(16)
        password_hash = hash_password(random_password)
        print(f"\nADMIN_PASSWORD_HASH={password_hash}")
        print(f"\nGenerated Password: {random_password}")
        print("\nIMPORTANT: Save this password! It won't be shown again.")
    
    print("\n" + "=" * 60)
    print("Add these to your .env file:")
    print("=" * 60)
    print(f"ADMIN_API_KEY={api_key}")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print("ADMIN_USERNAME=admin")
    print("=" * 60)


if __name__ == "__main__":
    main()
