from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
from pydantic import BaseModel
from app.database import get_db
from app.config import API_ACCESS_TOKEN_EXPIRE_MINUTES
from app.modules.users import models, schemas, service

router = APIRouter()

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = service.jwt.decode(token, service.API_SECRET_KEY, algorithms=[service.API_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except service.JWTError:
        raise credentials_exception
    user = service.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: models.User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Route d'authentification
# @router.post("/token", response_model=schemas.Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = service.authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = service.create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

#Route d'autentification
class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = service.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
# Routes pour les utilisateurs
@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_admin_user)):
    return service.create_user(db=db, user=user)

@router.get("/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_active_user)):
    users = service.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_active_user)):
    db_user = service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_admin_user)):
    return service.update_user(db=db, user_id=user_id, user=user)

@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(user_id: int, db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_admin_user)):
    return service.delete_user(db=db, user_id=user_id)

# Routes pour les rôles
@router.post("/roles/", response_model=schemas.Role)
async def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_admin_user)):
    return service.create_role(db=db, role=role)

@router.get("/roles/", response_model=List[schemas.Role])
async def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_active_user)):
    roles = service.get_roles(db, skip=skip, limit=limit)
    return roles

# Routes pour les bases de données gérées
@router.post("/databases/", response_model=schemas.ManagedDatabase)
async def create_database(database: schemas.ManagedDatabaseCreate, db: Session = Depends(get_db),
                         current_user: models.User = Depends(get_current_admin_user)):
    return service.create_database(db=db, database=database)

@router.get("/databases/", response_model=List[schemas.ManagedDatabase])
async def read_databases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_active_user)):
    databases = service.get_databases(db, skip=skip, limit=limit)
    return databases

# Routes pour la synchronisation des utilisateurs
@router.post("/sync-with-database/", response_model=schemas.UserDatabaseMapping)
async def sync_user_with_database(mapping: schemas.UserDatabaseMappingCreate, db: Session = Depends(get_db),
                                 current_user: models.User = Depends(get_current_admin_user)):
    return service.sync_user_with_database(db=db, mapping=mapping)