from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from .database import Base, engine, get_db
from .models import User
from .schemas import (
    LoginRequest,
    ProfileResponse,
    RegisterRequest,
    TokenResponse,
)


app = FastAPI()
Base.metadata.create_all(bind=engine)

oath2scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


@app.post(
    "/api/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    stmt = select(User).where(
        User.username == data.username
    )

    existing_user = db.scalar(stmt)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
    }


@app.post(
    "/api/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    stmt = select(User).where(
        User.username == data.username
    )

    user = db.scalar(stmt)

    if not user or not verify_password(
        data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


def get_current_user(
    token: str = Depends(oath2scheme),
    db: Session = Depends(get_db),
) -> User:

    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    stmt = select(User).where(User.id == int(user_id))
    user = db.scalar(stmt)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return user


@app.get(
    "/api/profile",
    response_model=ProfileResponse,
)
def profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": f"Welcome, {current_user.username}!"
    }