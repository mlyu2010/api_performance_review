"""
Database Initialization Script
==============================

This script initializes the PostgreSQL database for the Agents & Tasks API.
It performs the following operations:

1. Connects to the PostgreSQL database using Tortoise ORM
2. Generates database schemas for all models (users, agents, tasks, executions)
3. Creates a default admin user for testing and initial access

Usage
-----
Run this script before starting the application for the first time:
    python scripts/init_db.py

Default Credentials
------------------
Username: admin
Password: admin123
Email: admin@example.com

Notes
-----
- The script is idempotent - running it multiple times won't create duplicate users
- If the admin user already exists, it verifies the password and checks user status
- Database connection parameters are hardcoded for local development
- For production, consider using environment variables for database credentials
"""

import asyncio
from tortoise import Tortoise
from app.models.user import User


async def init_database():
    """
    Initialize the database with schemas and default admin user.

    This async function performs complete database initialization:
    - Establishes connection to PostgreSQL
    - Generates all table schemas from Tortoise ORM models
    - Creates or verifies the default admin user
    - Provides detailed status output for debugging

    The function includes comprehensive error handling and outputs
    detailed information about the created/existing user, including
    authentication instructions.

    Raises
    ------
    Exception
        If database connection fails or schema generation encounters errors.
        Full traceback is printed for debugging.

    Examples
    --------
    Run directly from command line:
        python scripts/init_db.py

    Or import and run programmatically:
        import asyncio
        from scripts.init_db import init_database
        asyncio.run(init_database())
    """
    try:
        print("Connecting to database...")
        await Tortoise.init(
            db_url="postgres://postgres:postgres@localhost:5432/agents_tasks_db",
            modules={"models": ["app.models"]},
        )
        print("Database connected successfully")

        await Tortoise.generate_schemas()
        print("Database schemas generated")

        # Create default test user
        existing_user = await User.filter(username="admin").first()
        if not existing_user:
            print("Creating default admin user...")
            new_user = await User.create(
                username="admin",
                email="admin@example.com",
                hashed_password=User.get_password_hash("admin123"),
                is_active=True
            )
            print("=" * 60)
            print("✓ Default user created successfully!")
            print("=" * 60)
            print(f"  Username:   admin")
            print(f"  Password:   admin123")
            print(f"  Email:      {new_user.email}")
            print(f"  User ID:    {new_user.id}")
            print(f"  Is Active:  {new_user.is_active}")
            print(f"  Created At: {new_user.created_at}")
            print("=" * 60)
            print("\nTo login, use:")
            print('  curl -X POST "http://localhost:8000/api/login" \\')
            print('    -H "Content-Type: application/json" \\')
            print('    -d \'{"username": "admin", "password": "admin123"}\'')
            print("=" * 60)
        else:
            print("=" * 60)
            print("Default admin user already exists")
            print("=" * 60)
            print(f"  Username:   {existing_user.username}")
            print(f"  Email:      {existing_user.email}")
            print(f"  User ID:    {existing_user.id}")
            print(f"  Is Active:  {existing_user.is_active}")
            print(f"  Deleted At: {existing_user.deleted_at}")
            print(f"  Created At: {existing_user.created_at}")
            print("=" * 60)

            # Verify password works
            if existing_user.verify_password("admin123"):
                print("✓ Password verification successful (admin123)")
            else:
                print("✗ WARNING: Password verification failed!")
                print("  The password may have been changed.")

            # Check if user is properly configured for authentication
            if not existing_user.is_active:
                print("✗ WARNING: User is NOT active!")
            if existing_user.deleted_at is not None:
                print("✗ WARNING: User is marked as DELETED!")

            print("=" * 60)

        await Tortoise.close_connections()
        print("\nDatabase connection closed")

    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
