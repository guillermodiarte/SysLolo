#rutas de login y registro
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from app.database import SessionLocal
from app.auth.auth_utils import authenticate_user, login_user, get_password_hash
from app.auth.dependencies import get_db
from app.models.models import User
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from app.routes import department_routes, reservation_routes, user_routes, reservation_cost_routes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter()

app = FastAPI(
    title="Dptos Lolo",
    description="Gestión de alojamientos",
    version="1.0.0"
)

app.include_router(reservation_routes.router)
app.include_router(department_routes.router)
app.include_router(user_routes.router)
app.include_router(reservation_cost_routes.router)

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "viewer"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db=Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"access_token": login_user(new_user), "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"access_token": login_user(user), "token_type": "bearer"}

@app.get("/me")
def read_current_user(token: str = Depends(oauth2_scheme)):
    return {"token": token}