from datetime import datetime, timedelta
from app.modules.monitoring.models import DatabaseMetric
from typing import List

class DatabaseAnalyzer:
    def __init__(self):
        pass

    def analyze_trends(self, db_name: str, period: str = 'daily') -> dict:
        """
        Analyse les tendances des métriques sur un certain période (par exemple: "daily", "weekly", "monthly").
        """
        end_time = datetime.utcnow()
        if period == 'daily':
            start_time = end_time - timedelta(days=1)
        elif period == 'weekly':
            start_time = end_time - timedelta(weeks=1)
        elif period == 'monthly':
            start_time = end_time - timedelta(weeks=4)
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'.")

        # Récupérer les métriques dans cette période pour la base de données donnée
        metrics = DatabaseMetric.objects.filter(
            db_name=db_name, 
            last_updated__gte=start_time, 
            last_updated__lte=end_time
        )

        # Calculer les tendances des différentes métriques
        trend = {
            'cpu_usage_trend': self.calculate_trend([m.cpu_usage for m in metrics]),
            'memory_usage_trend': self.calculate_trend([m.memory_usage for m in metrics]),
            'disk_usage_trend': self.calculate_trend([m.disk_usage for m in metrics]),
            'database_size_trend': self.calculate_trend([m.database_size_mb for m in metrics]),
        }

        return trend

    def calculate_trend(self, values: List[float]) -> dict:
        """
        Calcule la tendance des valeurs (peut être basé sur la moyenne, l'écart type, ou tout autre critère).
        """
        if not values:
            return {
                'average': 0,
                'min': 0,
                'max': 0,
                'std_dev': 0
            }

        avg = sum(values) / len(values)
        min_value = min(values)
        max_value = max(values)
        std_dev = (sum((x - avg) ** 2 for x in values) / len(values)) ** 0.5

        return {
            'average': avg,
            'min': min_value,
            'max': max_value,
            'std_dev': std_dev
        }

    def generate_alerts(self, db_name: str) -> List[str]:
        """
        Génère des alertes si certaines conditions sont dépassées (par exemple, CPU trop élevé, mémoire insuffisante).
        """
        alerts = []
        metrics = DatabaseMetric.objects.filter(db_name=db_name).order_by('-last_updated')[:10]

        for metric in metrics:
            if metric.cpu_usage > 85.0:
                alerts.append(f"ALERT: High CPU usage on {db_name}. Current: {metric.cpu_usage}%")
            if metric.memory_usage > 80.0:
                alerts.append(f"ALERT: High memory usage on {db_name}. Current: {metric.memory_usage}%")
            if metric.disk_usage > 90.0:
                alerts.append(f"ALERT: High disk usage on {db_name}. Current: {metric.disk_usage}%")
            if metric.database_size_mb > 1024:  # 1 GB
                alerts.append(f"ALERT: Database size large on {db_name}. Current: {metric.database_size_mb} MB")

        return alerts
