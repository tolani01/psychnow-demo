"""
Database Initialization
Seeds initial data including admin user
"""
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings


def init_db(db: Session) -> None:
    """
    Initialize database with seed data
    
    Creates:
    - Default admin user
    - System consents (versions)
    """
    # Check if admin user already exists
    admin = db.query(User).filter(
        User.email == "admin@psychnow.com",
        User.role == UserRole.ADMIN
    ).first()
    
    if not admin:
        print("Creating default admin user...")
        admin = User(
            email="admin@psychnow.com",
            hashed_password=get_password_hash("Admin123!"),  # Change this in production!
            role=UserRole.ADMIN,
            first_name="System",
            last_name="Administrator",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"[OK] Admin user created:")
        print(f"   Email: admin@psychnow.com")
        print(f"   Password: Admin123!")
        print(f"   [WARNING] CHANGE THIS PASSWORD IN PRODUCTION!")
    else:
        print("Admin user already exists")
    
    print("[OK] Database initialization complete")


def get_or_create_admin(db: Session) -> User:
    """
    Get existing admin or create one
    
    Returns:
        Admin user
    """
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    
    if not admin:
        init_db(db)
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    
    return admin

