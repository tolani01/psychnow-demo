"""
Authentication Endpoints
User registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User, UserRole
from app.models.provider_profile import ProviderProfile
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.deps import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/create-demo-user", response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_demo_user(db: Session = Depends(get_db)):
    """
    Create a demo user for testing purposes
    """
    demo_email = "demo@demo.com"
    
    # Check if demo user already exists
    existing_user = db.query(User).filter(User.email == demo_email).first()
    if existing_user:
        # Return existing demo user
        access_token = create_access_token(data={"sub": str(existing_user.id)})
        return Token(access_token=access_token)
    
    # Create demo user
    db_user = User(
        email=demo_email,
        hashed_password=get_password_hash("demo"),
        role=UserRole.PATIENT,
        first_name="Demo",
        last_name="User",
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return Token(access_token=access_token)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user (patient or provider)
    
    For providers: account is created with pending approval status
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    db_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # If provider, create provider profile with pending status
    if user_data.role == UserRole.PROVIDER:
        provider_profile = ProviderProfile(
            user_id=db_user.id,
            approval_status="pending"
        )
        db.add(provider_profile)
        db.commit()
    
    return db_user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login and receive JWT access token
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check if provider is approved
    if user.role == UserRole.PROVIDER:
        provider_profile = db.query(ProviderProfile).filter(
            ProviderProfile.user_id == user.id
        ).first()
        
        if provider_profile and provider_profile.approval_status != "approved":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Provider account is {provider_profile.approval_status}. Please wait for admin approval."
            )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return current_user

