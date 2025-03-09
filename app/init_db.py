from app.database import SessionLocal, engine, Base
from app.modules.users.models import Role, User
from app.modules.users.service import get_password_hash

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Vérifier si des rôles existent déjà
    if db.query(Role).count() == 0:
        # Créer les rôles de base
        roles = [
            Role(name="admin", description="Full administrator access"),
            Role(name="dba", description="Database administrator"),
            Role(name="user", description="Regular user"),
            Role(name="read_only", description="Read-only access")
        ]
        db.add_all(roles)
        db.commit()
    
    # Vérifier si un super-utilisateur existe déjà
    if db.query(User).filter(User.is_superuser == True).count() == 0:
        # Créer un super-utilisateur initial
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        
        if admin_role:
            admin_user = User(
                username="admin",
                email="admin@gmail.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrator",
                is_active=True,
                is_superuser=True
            )
            admin_user.roles = [admin_role]
            db.add(admin_user)
            db.commit()
    
    db.close()

if __name__ == "__main__":
    init_db()