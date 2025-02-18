# app/modules/users/router.py
from fastapi import APIRouter

# Création du router pour les utilisateurs
router = APIRouter()

# Exemple de route pour obtenir la liste des utilisateurs
@router.get("/")
async def get_users():
    return {"message": "Liste des utilisateurs"}
