import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from statistics import mean, stdev
from enum import Enum

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(Enum):
    HIGH_CPU = "high_cpu_usage"
    HIGH_MEMORY = "high_memory_usage"
    HIGH_CONNECTIONS = "high_connections"
    HIGH_LATENCY = "high_query_latency"
    CONNECTION_ISSUE = "connection_issue"
    STORAGE_CRITICAL = "storage_critical"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SYSTEM_OVERLOAD = "system_overload"

class MetricAnalyzer:
    def __init__(self, 
                 connection_id: int, 
                 db_type: str,
                 thresholds: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize metrics analyzer with thresholds
        
        Args:
            connection_id: Database connection ID
            db_type: Type of database (mysql, mongodb, oracle)
            thresholds: Dictionary of thresholds for different metrics
        """
        self.connection_id = connection_id
        self.db_type = db_type
        if db_type not in ["mysql", "mongodb", "oracle"]:
            raise ValueError("Invalid database type. Must be one of: mysql, mongodb, oracle")
        
        # Default thresholds if not provided
        self.thresholds = thresholds or {
            "cpu_usage": {
                "warning": 70.0,
                "critical": 90.0
            },
            "memory_usage": {
                "warning": 75.0,
                "critical": 90.0
            },
            "disk_usage": {
                "warning": 80.0,
                "critical": 90.0
            },
            "connections_count": {
                "warning": 100,
                "critical": 200
            },
            "query_latency": {
                "warning": 1.0,  # seconds
                "critical": 5.0   # seconds
            }
        }
        
        # Keep history of recent metrics for trend analysis
        self.metrics_history = []
        self.max_history_size = 100  # Keep last 100 data points
        
    def add_metrics_to_history(self, metrics: Dict[str, Any]) -> None:
        """Add metrics to historical data for trend analysis"""
        if len(self.metrics_history) >= self.max_history_size:
            self.metrics_history.pop(0)  # Remove oldest element
        
        self.metrics_history.append(metrics)
    
    def analyze_metrics(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze metrics and return list of alerts if thresholds are exceeded
        
        Args:
            current_metrics: Current metrics collected from database
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Add current metrics to history
        self.add_metrics_to_history(current_metrics)
        
        # Check if there was an error collecting metrics
        if "error" in current_metrics:
            alerts.append({
                "connection_id": self.connection_id,
                "alert_type": AlertType.CONNECTION_ISSUE.value,
                "severity": AlertSeverity.CRITICAL.value,
                "message": f"Connection issue: {current_metrics['error']}",
                "timestamp": datetime.utcnow(),
                "metrics": current_metrics
            })
            return alerts
            
        # Check CPU usage
        if current_metrics.get("cpu_usage") is not None:
            cpu_usage = current_metrics["cpu_usage"]
            if cpu_usage >= self.thresholds["cpu_usage"]["critical"]:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.HIGH_CPU.value,
                    "severity": AlertSeverity.CRITICAL.value,
                    "message": f"Critical CPU usage: {cpu_usage}%",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"cpu_usage": cpu_usage}
                })
            elif cpu_usage >= self.thresholds["cpu_usage"]["warning"]:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.HIGH_CPU.value,
                    "severity": AlertSeverity.WARNING.value,
                    "message": f"High CPU usage: {cpu_usage}%",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"cpu_usage": cpu_usage}
                })
        
        # Check memory usage
        if current_metrics.get("memory_usage") is not None:
            memory_usage = current_metrics["memory_usage"]
            if memory_usage >= self.thresholds["memory_usage"]["critical"]:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.HIGH_MEMORY.value,
                    "severity": AlertSeverity.CRITICAL.value,
                    "message": f"Critical memory usage: {memory_usage}%",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"memory_usage": memory_usage}
                })
            elif memory_usage >= self.thresholds["memory_usage"]["warning"]:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.HIGH_MEMORY.value,
                    "severity": AlertSeverity.WARNING.value,
                    "message": f"High memory usage: {memory_usage}%",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"memory_usage": memory_usage}
                })
        
        # Check connections count
        if current_metrics.get("connections_count") is not None:
            connections = current_metrics["connections_count"]
            if connections >= self.thresholds["connections_count"]["critical"]:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.HIGH_CONNECTIONS.value,
                    "severity": AlertSeverity.CRITICAL.value,
                    "message": f"Critical number of connections: {connections}",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"connections_count": connections}
                })
            elif connections >= self.thresholds["connections_count"]["warning"]:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.HIGH_CONNECTIONS.value,
                    "severity": AlertSeverity.WARNING.value,
                    "message": f"High number of connections: {connections}",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"connections_count": connections}
                })
                
        # Check query latency
        if current_metrics.get("query_latency") is not None:
            latency = current_metrics["query_latency"]
            if latency >= self.thresholds["query_latency"]["critical"]:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.HIGH_LATENCY.value,
                    "severity": AlertSeverity.CRITICAL.value,
                    "message": f"Critical query latency: {latency:.2f}s",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"query_latency": latency}
                })
            elif latency >= self.thresholds["query_latency"]["warning"]:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.HIGH_LATENCY.value,
                    "severity": AlertSeverity.WARNING.value,
                    "message": f"High query latency: {latency:.2f}s",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"query_latency": latency}
                })
        
        # Analyze trends if we have enough history
        if len(self.metrics_history) >= 5:
            trend_alerts = self.analyze_trends()
            alerts.extend(trend_alerts)
        
        return alerts
    
    def analyze_trends(self) -> List[Dict[str, Any]]:
        """Analyze trends in metrics history"""
        alerts = []
        
        # Only analyze if we have sufficient data points
        if len(self.metrics_history) < 5:
            return alerts
        
        # Get the last 5 data points for trend analysis
        recent_metrics = self.metrics_history[-5:]
        
        # Analyze CPU trend
        cpu_values = [m.get("cpu_usage") for m in recent_metrics if m.get("cpu_usage") is not None]
        if len(cpu_values) >= 5:
            if self._is_consistently_increasing(cpu_values) and cpu_values[-1] > self.thresholds["cpu_usage"]["warning"] * 0.8:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.PERFORMANCE_DEGRADATION.value,
                    "severity": AlertSeverity.WARNING.value,
                    "message": f"CPU usage trending upward: {cpu_values[-1]:.2f}% (last 5 readings: {', '.join([f'{v:.2f}%' for v in cpu_values])})",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"cpu_trend": cpu_values}
                })
        
        # Analyze memory trend
        memory_values = [m.get("memory_usage") for m in recent_metrics if m.get("memory_usage") is not None]
        if len(memory_values) >= 5:
            if self._is_consistently_increasing(memory_values) and memory_values[-1] > self.thresholds["memory_usage"]["warning"] * 0.8:
                alerts.append({
                    "connection_id": self.connection_id,
                    "alert_type": AlertType.PERFORMANCE_DEGRADATION.value,
                    "severity": AlertSeverity.WARNING.value,
                    "message": f"Memory usage trending upward: {memory_values[-1]:.2f}% (last 5 readings: {', '.join([f'{v:.2f}%' for v in memory_values])})",
                    "timestamp": datetime.utcnow(),
                    "metrics": {"memory_trend": memory_values}
                })
        
        # System overload detection - multiple high metrics simultaneously
        latest = self.metrics_history[-1]
        high_metrics_count = 0
        
        if latest.get("cpu_usage", 0) > self.thresholds["cpu_usage"]["warning"]:
            high_metrics_count += 1
        if latest.get("memory_usage", 0) > self.thresholds["memory_usage"]["warning"]:
            high_metrics_count += 1
        if latest.get("connections_count", 0) > self.thresholds["connections_count"]["warning"]:
            high_metrics_count += 1
        if latest.get("query_latency", 0) > self.thresholds["query_latency"]["warning"]:
            high_metrics_count += 1
            
        if high_metrics_count >= 3:
            alerts.append({
                "connection_id": self.connection_id,
                "alert_type": AlertType.SYSTEM_OVERLOAD.value,
                "severity": AlertSeverity.CRITICAL.value,
                "message": f"System overload detected: multiple metrics at warning levels",
                "timestamp": datetime.utcnow(),
                "metrics": {
                    "cpu_usage": latest.get("cpu_usage"),
                    "memory_usage": latest.get("memory_usage"),
                    "connections_count": latest.get("connections_count"),
                    "query_latency": latest.get("query_latency")
                }
            })
            
        return alerts
    
    def _is_consistently_increasing(self, values: List[float]) -> bool:
        """Check if values are consistently increasing"""
        if len(values) < 3:
            return False
            
        # Calculate differences between consecutive values
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # Count positive differences
        positive_diffs = sum(1 for diff in diffs if diff > 0)
        
        # Consider it increasing if at least 75% of differences are positive
        return positive_diffs / len(diffs) >= 0.75

    def generate_health_score(self, metrics: Dict[str, Any]) -> float:
        """
        Generate a health score from 0 to 100
        0 = critical issues, 100 = perfectly healthy
        """
        if "error" in metrics:
            return 0.0
            
        scores = []
        
        # CPU score
        if metrics.get("cpu_usage") is not None:
            cpu = metrics["cpu_usage"]
            if cpu >= self.thresholds["cpu_usage"]["critical"]:
                scores.append(0)
            elif cpu >= self.thresholds["cpu_usage"]["warning"]:
                # Linear interpolation between warning and critical
                cpu_score = 50 - 50 * (cpu - self.thresholds["cpu_usage"]["warning"]) / (
                    self.thresholds["cpu_usage"]["critical"] - self.thresholds["cpu_usage"]["warning"]
                )
                scores.append(cpu_score)
            else:
                # Linear interpolation between 0 and warning
                cpu_score = 100 - 50 * cpu / self.thresholds["cpu_usage"]["warning"]
                scores.append(cpu_score)
        
        # Memory score
        if metrics.get("memory_usage") is not None:
            memory = metrics["memory_usage"]
            if memory >= self.thresholds["memory_usage"]["critical"]:
                scores.append(0)
            elif memory >= self.thresholds["memory_usage"]["warning"]:
                memory_score = 50 - 50 * (memory - self.thresholds["memory_usage"]["warning"]) / (
                    self.thresholds["memory_usage"]["critical"] - self.thresholds["memory_usage"]["warning"]
                )
                scores.append(memory_score)
            else:
                memory_score = 100 - 50 * memory / self.thresholds["memory_usage"]["warning"]
                scores.append(memory_score)
        
        # Other metrics can be added similarly...
        
        # Return average score, or 0 if no scores
        if not scores:
            return 100.0  # Default to healthy if no metrics to score
        
        return sum(scores) / len(scores)
    
    def get_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        if "error" in metrics:
            recommendations.append("Check database connectivity and credentials")
            return recommendations
            
        # CPU recommendations
        if metrics.get("cpu_usage", 0) > self.thresholds["cpu_usage"]["warning"]:
            recommendations.append("Review query performance and optimize high-CPU queries")
            recommendations.append("Consider increasing CPU resources if trend continues")
        
        # Memory recommendations
        if metrics.get("memory_usage", 0) > self.thresholds["memory_usage"]["warning"]:
            if self.db_type == "mysql":
                recommendations.append("Review MySQL buffer pool configuration")
            elif self.db_type == "mongodb":
                recommendations.append("Consider increasing MongoDB WiredTiger cache size")
            elif self.db_type == "oracle":
                recommendations.append("Review Oracle SGA/PGA memory allocation")
            recommendations.append("Check for memory leaks or excessive caching")
        
        # Connection recommendations
        if metrics.get("connections_count", 0) > self.thresholds["connections_count"]["warning"]:
            if metrics["connections_count"] > self.thresholds["connections_count"]["critical"]:
                recommendations.append("Critique : Trop de connexions actives. Vérifiez les sessions inutilisées et optimisez la gestion des connexions.")
            else:
                recommendations.append("Attention : Le nombre de connexions commence à être élevé. Surveillez l'activité et envisagez d'optimiser les requêtes.")

        # CPU usage recommendations
        if metrics.get("cpu_usage", 0) > self.thresholds["cpu_usage"]["warning"]:
            if metrics["cpu_usage"] > self.thresholds["cpu_usage"]["critical"]:
                recommendations.append("Critique : L'utilisation du CPU est très élevée. Envisagez d'optimiser les requêtes ou de mettre à niveau les ressources du serveur.")
            else:
                recommendations.append("Attention : L'utilisation du CPU est au-dessus du seuil recommandé. Analysez les charges de travail.")

        # Memory usage recommendations
        if metrics.get("memory_usage", 0) > self.thresholds["memory_usage"]["warning"]:
            if metrics["memory_usage"] > self.thresholds["memory_usage"]["critical"]:
                recommendations.append("Critique : La mémoire est presque saturée. Vérifiez les processus gourmands et envisagez d'ajouter de la RAM.")
            else:
                recommendations.append("Attention : La consommation mémoire est élevée. Optimisez les requêtes et la gestion du cache.")

        # Disk usage recommendations
        if metrics.get("disk_usage", 0) > self.thresholds["disk_usage"]["warning"]:
            if metrics["disk_usage"] > self.thresholds["disk_usage"]["critical"]:
                recommendations.append("Critique : L'espace disque est presque plein. Libérez de l'espace ou ajoutez du stockage.")
            else:
                recommendations.append("Attention : L'utilisation du disque est élevée. Supprimez les fichiers inutiles et surveillez l'évolution.")

        return recommendations
    
    def save_metrics_history(self, storage_service):
        """Sauvegarde l'historique des métriques dans la base de données"""
        storage_service.save_metrics_history(self.connection_id, self.metrics_history)

@classmethod
def load_metrics_history(cls, connection_id, db_type, thresholds, storage_service):
    """Charge l'historique des métriques depuis la base de données"""
    analyzer = cls(connection_id, db_type, thresholds)
    analyzer.metrics_history = storage_service.get_metrics_history(connection_id)
    return analyzer

def detect_anomalies(self, metric_name, sensitivity=2.0):
    """
    Détecte les anomalies en utilisant l'écart-type
    
    Args:
        metric_name: Nom de la métrique à analyser
        sensitivity: Multiplicateur d'écart-type (2.0 = 95% de confiance)
    """
    values = [m.get(metric_name) for m in self.metrics_history 
             if m.get(metric_name) is not None]
    
    if len(values) < 10:  # Besoin d'assez de données
        return []
    
    avg = mean(values)
    std_dev = stdev(values) if len(values) > 1 else 0
    threshold = avg + (sensitivity * std_dev)
    
    anomalies = []
    for i, val in enumerate(values):
        if val > threshold:
            anomalies.append({
                'index': i,
                'value': val,
                'timestamp': self.metrics_history[i]['timestamp'],
                'deviation': (val - avg) / std_dev if std_dev > 0 else 0
            })
    
    return anomalies
     


def find_metric_correlations(self):
    """Trouve les corrélations entre différentes métriques"""
    metrics_to_analyze = ['cpu_usage', 'memory_usage', 'connections_count', 'query_latency']
    results = {}
    
    for m1 in metrics_to_analyze:
        for m2 in metrics_to_analyze:
            if m1 != m2:
                correlation = self._calculate_correlation(m1, m2)
                if abs(correlation) > 0.7:  # Forte corrélation
                    results[f"{m1}-{m2}"] = correlation
    
    return results

def _calculate_correlation(self, metric1, metric2):
    """Calcule le coefficient de corrélation entre deux métriques"""
    values1 = []
    values2 = []
    
    for m in self.metrics_history:
        if m.get(metric1) is not None and m.get(metric2) is not None:
            values1.append(m.get(metric1))
            values2.append(m.get(metric2))
    
    if len(values1) < 5:
        return 0
        
    # Utilisez numpy pour calculer la corrélation
    return np.corrcoef(values1, values2)[0, 1]
def predict_future_value(self, metric_name, hours_ahead=24):
    """
    Prédit la valeur future d'une métrique basée sur la tendance actuelle
    Utilise une régression linéaire simple
    """
    values = [(i, m.get(metric_name)) 
             for i, m in enumerate(self.metrics_history) 
             if m.get(metric_name) is not None]
    
    if len(values) < 5:
        return None
    
    x = np.array([v[0] for v in values])
    y = np.array([v[1] for v in values])
    
    # Régression linéaire simple
    slope, intercept = np.polyfit(x, y, 1)
    
    # Prédire la valeur future
    next_x = len(self.metrics_history) + (hours_ahead * 3600 / self.collection_interval)
    predicted_value = slope * next_x + intercept
    
    return {
        'current': y[-1],
        'predicted': predicted_value,
        'change_percentage': ((predicted_value - y[-1]) / y[-1]) * 100 if y[-1] != 0 else 0,
        'hours_ahead': hours_ahead
    }


def adapt_thresholds(self, learning_rate=0.1):
    """Adapte les seuils en fonction des données historiques"""
    if len(self.metrics_history) < 20:
        return  # Pas assez de données
    
    for metric_name in ['cpu_usage', 'memory_usage', 'connections_count']:
        values = [m.get(metric_name) for m in self.metrics_history 
                 if m.get(metric_name) is not None]
        
        if not values:
            continue
            
        # Calcul du 95e percentile
        p95 = np.percentile(values, 95)
        
        # Ajustement du seuil d'avertissement
        current_warning = self.thresholds.get(metric_name, {}).get('warning')
        if current_warning and p95 < current_warning * 0.7:
            # Si le 95e percentile est bien inférieur au seuil, réduire le seuil
            new_warning = current_warning - (current_warning - p95) * learning_rate
            self.thresholds[metric_name]['warning'] = new_warning
        elif p95 > current_warning:
            # Si le 95e percentile dépasse le seuil, augmenter légèrement
            new_warning = current_warning + (p95 - current_warning) * learning_rate
            self.thresholds[metric_name]['warning'] = min(new_warning, 
                                                        self.thresholds[metric_name]['critical'] * 0.9)
