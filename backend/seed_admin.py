"""
Seed Admin User
Run this script once to create the initial admin account
"""
from app.db.session import SessionLocal
from app.db.init_db import init_db


def main():
    """Seed the database with admin user"""
    print("[SEED] Seeding database with admin user...\n")
    
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    
    print("\n[OK] Seeding complete!")
    print("\nYou can now login as admin:")
    print("  Email: admin@psychnow.com")
    print("  Password: Admin123!")


if __name__ == "__main__":
    main()

