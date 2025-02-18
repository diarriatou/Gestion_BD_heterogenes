from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .modules.users.router import router as users_router
# from app.modules.monitoring.router import router as monitoring_router
# from app.modules.backups.router import router as backups_router
from app.database import engine, Base

# Création des tables dans la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DB Management Platform",
    description="Plateforme centralisée pour la gestion de bases de données hétérogènes",
    version="0.1.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(users_router, prefix="/api/users", tags=["Users"])
# app.include_router(monitoring_router, prefix="/api/monitoring", tags=["Monitoring"])
# app.include_router(backups_router, prefix="/api/backups", tags=["Backups"])


@app.get("/")
async def root():
    return {"message": "Bienvenue sur la plateforme de gestion des bases de données"}