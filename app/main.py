from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.modules.monitoring.scheduler import start_scheduler
import logging
from .modules.users.router import router as users_router
from app.modules.monitoring.router import router as monitoring_router
from app.modules.backups.router import router as backups_router
from app.database import engine, Base

# Création des tables dans la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DB Management Platform",
    description="Plateforme centralisée pour la gestion de bases de données hétérogènes",
    version="0.1.0"
)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurez les origines autorisées (plus permissif pour debug)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Au cas où React utilise un autre port
    "http://127.0.0.1:3001",
]

# Configuration CORS avec plus d'options
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Middleware pour logger les requêtes (optionnel, pour debug)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"🌐 {request.method} {request.url}")
    logger.info(f"📋 Origin: {request.headers.get('origin', 'No origin')}")
    
    response = await call_next(request)
    
    logger.info(f"✅ Response: {response.status_code}")
    return response

# Inclusion des routers
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(monitoring_router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(backups_router, prefix="/api/backups", tags=["Backups"])

# Start metrics collection scheduler
@app.on_event("startup")
def startup_event():
    logger.info("🚀 Starting application...")
    scheduler = start_scheduler()
    app.state.scheduler = scheduler

@app.on_event("shutdown")
def shutdown_event():
    logger.info("🛑 Shutting down application...")
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown()

@app.get("/")
async def root():
    return {"message": "Bienvenue sur la plateforme de gestion des bases de données"}

# Endpoint de test CORS
@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS fonctionne!", "timestamp": "2024-01-01"}