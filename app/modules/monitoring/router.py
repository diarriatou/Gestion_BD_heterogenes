from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.modules.monitoring.schemas import DatabaseMetricSchema
from app.modules.monitoring.models import DatabaseMetric  
from app.modules.monitoring.analyzer import DatabaseAnalyzer

router = APIRouter()

# Route pour obtenir toutes les métriques de bases de données
@router.get("/metrics", response_model=List[DatabaseMetricSchema])
async def get_metrics():
    try:
        # Ici, vous récupérez les données de votre base de données (MySQL ou autre)
        metrics = DatabaseMetric.objects.all()  # Adapté selon votre ORM
        return [metric.to_dict() for metric in metrics]  # Convertissez les objets en dictionnaires
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques : {str(e)}")

# Route pour obtenir une métrique spécifique
@router.get("/metrics/{db_name}", response_model=DatabaseMetricSchema)
async def get_metric(db_name: str):
    try:
        # Récupérez la métrique pour une base spécifique
        metric = DatabaseMetric.objects.get(db_name=db_name)  # Adapté selon votre ORM
        return metric.to_dict()
    except DatabaseMetric.DoesNotExist:
        raise HTTPException(status_code=404, detail="Métrique de base de données non trouvée")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la métrique : {str(e)}")

# Route pour ajouter une nouvelle métrique
@router.post("/metrics", response_model=DatabaseMetricSchema)
async def add_metric(metric: DatabaseMetricSchema):
    try:
        # Convertissez l'objet en format adapté pour insertion dans la base
        new_metric = DatabaseMetric(**metric.dict())  # Assurez-vous que votre modèle ORM accepte ce format
        new_metric.save()  # Sauvegardez dans la base de données
        return new_metric.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout de la métrique : {str(e)}")

# Route pour mettre à jour une métrique existante
@router.put("/metrics/{db_name}", response_model=DatabaseMetricSchema)
async def update_metric(db_name: str, metric: DatabaseMetricSchema):
    try:
        # Mettez à jour la métrique pour la base spécifiée
        existing_metric = DatabaseMetric.objects.get(db_name=db_name)  # Adapté selon votre ORM
        for key, value in metric.dict().items():
            setattr(existing_metric, key, value)
        existing_metric.save()
        return existing_metric.to_dict()
    except DatabaseMetric.DoesNotExist:
        raise HTTPException(status_code=404, detail="Métrique de base de données non trouvée")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la métrique : {str(e)}")
@router.get("/metrics/{db_name}/trends", response_model=dict)
async def get_trends(db_name: str, period: str = 'daily'):
    analyzer = DatabaseAnalyzer()
    try:
        trend = analyzer.analyze_trends(db_name, period)
        return trend
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse des tendances : {str(e)}")

# Route pour générer des alertes pour une base de données
@router.get("/metrics/{db_name}/alerts", response_model=List[str])
async def get_alerts(db_name: str):
    analyzer = DatabaseAnalyzer()
    try:
        alerts = analyzer.generate_alerts(db_name)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des alertes : {str(e)}")