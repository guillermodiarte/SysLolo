#(registro y login)
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import models
from app.auth.security import create_access_token
from datetime import timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def login_user(user: models.User):
    token_data = {"sub": user.username, "role": user.role}
    return create_access_token(token_data, timedelta(minutes=60))
