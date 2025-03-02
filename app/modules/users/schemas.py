from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# Schémas pour Role
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
    
    class Config:
        from_attributes = True

# Schémas pour ManagedDatabase
class ManagedDatabaseBase(BaseModel):
    name: str
    db_type: str
    host: str
    port: int
    username: str
    database_name: str
    description: Optional[str] = None

class ManagedDatabaseCreate(ManagedDatabaseBase):
    password: str

class ManagedDatabase(ManagedDatabaseBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attibutes = True
    '''validateurs pour verifier le type de la base de données'''
    @validator('db_type')
    def db_type_must_be_valid(cls, v):
        if v.lower() not in ['mysql', 'oracle', 'mongodb']:
            raise ValueError('Invalid database type')
        return v

# Schémas pour User
class UserBase(BaseModel):
    # username: str = Field(..., description="Unique username for the user")
    email: EmailStr = Field(..., description="Email address of the user")
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    roles: List[int] = []

class UserUpdate(BaseModel):
    # username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    roles: Optional[List[int]] = None

class User(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: List[Role] = []
    
    class Config:
        from_attributes = True

# Schémas pour UserDatabaseMapping
class UserDatabaseMappingBase(BaseModel):
    platform_user_id: int
    database_id: int
    database_username: str
    database_roles: List[str] = []
    
    @validator('database_roles', pre=True)
    def parse_database_roles(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

class UserDatabaseMappingCreate(UserDatabaseMappingBase):
    pass

class UserDatabaseMapping(UserDatabaseMappingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes= True

# Schéma pour authentification
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None