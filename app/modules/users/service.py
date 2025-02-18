from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import json

from app.config import API_SECRET_KEY, API_ALGORITHM, API_ACCESS_TOKEN_EXPIRE_MINUTES
from app.modules.users import models, schemas
from app.adapters.mysql_adapter import MySQLAdapter
from app.adapters.oracle_adapter import OracleAdapter
from app.adapters.mongo_adapter import MongoAdapter

# Configuration de l'encryption des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET_KEY, algorithm=API_ALGORITHM)
    return encoded_jwt

# Service CRUD pour User
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    
    # Vérifier si l'utilisateur existe déjà
    db_user_username = get_user_by_username(db, username=user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user_email = get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Créer l'utilisateur
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Ajouter les rôles
    if user.roles:
        roles = db.query(models.Role).filter(models.Role.id.in_(user.roles)).all()
        db_user.roles = roles
        db.commit()
        db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mettre à jour les champs fournis
    user_data = user.dict(exclude_unset=True)
    if 'password' in user_data:
        user_data['hashed_password'] = get_password_hash(user_data.pop('password'))
    
    # Traiter les rôles séparément
    roles = user_data.pop('roles', None)
    
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    if roles is not None:
        db_roles = db.query(models.Role).filter(models.Role.id.in_(roles)).all()
        db_user.roles = db_roles
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return db_user

# Service CRUD pour Role
def get_role(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Role).offset(skip).limit(limit).all()

def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# Service CRUD pour ManagedDatabase
def get_database(db: Session, database_id: int):
    return db.query(models.ManagedDatabase).filter(models.ManagedDatabase.id == database_id).first()

def get_databases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ManagedDatabase).offset(skip).limit(limit).all()

def create_database(db: Session, database: schemas.ManagedDatabaseCreate):
    db_database = models.ManagedDatabase(**database.dict())
    db.add(db_database)
    db.commit()
    db.refresh(db_database)
    return db_database

# Service pour synchroniser les utilisateurs avec les bases de données externes
def sync_user_with_database(db: Session, mapping: schemas.UserDatabaseMappingCreate):
    # Récupérer l'utilisateur et la base de données
    user = get_user(db, mapping.platform_user_id)
    database = get_database(db, mapping.database_id)
    
    if not user or not database:
        raise HTTPException(status_code=404, detail="User or database not found")
    
    # Créer le mapping dans la base centrale
    db_mapping = models.UserDatabaseMapping(
        platform_user_id=mapping.platform_user_id,
        database_id=mapping.database_id,
        database_username=mapping.database_username,
        database_roles=json.dumps(mapping.database_roles)
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    
    # Créer l'utilisateur dans la base de données externe
    if database.db_type == 'mysql':
        adapter = MySQLAdapter(
            host=database.host,
            port=database.port,
            user=database.username,
            password=database.password,
            database=database.database_name
        )
    elif database.db_type == 'oracle':
        adapter = OracleAdapter(
            host=database.host,
            port=database.port,
            user=database.username,
            password=database.password,
            sid=database.database_name
        )
    elif database.db_type == 'mongodb':
        adapter = MongoAdapter(
            host=database.host,
            port=database.port,
            user=database.username,
            password=database.password,
            database=database.database_name
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported database type: {database.db_type}")
    
    # Se connecter et créer l'utilisateur
    if not adapter.connect():
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    success = adapter.create_user(
        username=mapping.database_username,
        password=user.username,  # Utilisation d'un mot de passe temporaire que l'utilisateur devra changer
        roles=mapping.database_roles
    )
    
    if not success:
        db.delete(db_mapping)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to create user in the external database")
    
    return db_mapping