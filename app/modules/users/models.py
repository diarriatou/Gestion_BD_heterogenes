from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base

# Table d'association pour la relation many-to-many entre utilisateurs et rôles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

# Table d'association pour la relation many-to-many entre utilisateurs et bases de données
user_databases = Table(
    'user_databases',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('database_id', Integer, ForeignKey('managed_databases.id'))
)

class User(Base):
    """Utilisateurs de la plateforme"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    databases = relationship("ManagedDatabase", secondary=user_databases, back_populates="users")
    
    def __repr__(self):
        return f"<User {self.username}>"

class Role(Base):
    """Rôles disponibles dans la plateforme"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200))
    
    # Relations
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"

class ManagedDatabase(Base):
    """Bases de données gérées par la plateforme"""
    __tablename__ = "managed_databases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    db_type = Column(String(50), nullable=False)  # mysql, oracle, mongodb
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    database_name = Column(String(100), nullable=False)
    description = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    users = relationship("User", secondary=user_databases, back_populates="databases")
    
    def __repr__(self):
        return f"<ManagedDatabase {self.name} ({self.db_type})>"

class UserDatabaseMapping(Base):
    """Mapping entre utilisateurs de la plateforme et utilisateurs des bases de données"""
    __tablename__ = "user_database_mappings"

    id = Column(Integer, primary_key=True, index=True)
    platform_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    database_id = Column(Integer, ForeignKey("managed_databases.id"), nullable=False)
    database_username = Column(String(50), nullable=False)
    database_roles = Column(String(200))  # Stocké comme JSON string
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserDatabaseMapping platform_user={self.platform_user_id} database={self.database_id}>"