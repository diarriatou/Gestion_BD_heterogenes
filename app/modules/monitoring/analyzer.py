from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
import logging
from app.modules.monitoring.models import Metric, Alert, AlertRule, DatabaseConnection

logger = logging.getLogger(__name__)

class MetricAnalyzer:
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_metrics(self, db_id: int, metrics: Dict[str, Any]) -> List[Alert]:
        """
        Analyze collected metrics against alert rules and generate alerts if needed.
        
        Args:
            db_id: Database connection ID
            metrics: Dictionary of collected metrics
            
        Returns:
            List of generated alerts
        """
        # Get all alert rules for this database
        rules = self.db.query(AlertRule).filter(
            AlertRule.database_id == db_id,
            AlertRule.enabled == True
        ).all()
        
        generated_alerts = []
        
        for rule in rules:
            # Get the metric value if it exists
            if rule.metric_name not in metrics or metrics[rule.metric_name] is None:
                continue
                
            metric_value = metrics[rule.metric_name]
            threshold_exceeded = False
            
            # Check if threshold is exceeded based on comparison operator
            if rule.comparison == ">":
                threshold_exceeded = metric_value > rule.threshold
            elif rule.comparison == "<":
                threshold_exceeded = metric_value < rule.threshold
            elif rule.comparison == ">=":
                threshold_exceeded = metric_value >= rule.threshold
            elif rule.comparison == "<=":
                threshold_exceeded = metric_value <= rule.threshold
            elif rule.comparison == "==":
                threshold_exceeded = metric_value == rule.threshold
            
            if threshold_exceeded:
                # Get database name for the alert message
                db_connection = self.db.query(DatabaseConnection).filter(
                    DatabaseConnection.id == db_id
                ).first()
                
                db_name = db_connection.name if db_connection else f"Database ID {db_id}"
                
                # Create alert message
                message = f"{db_name}: {rule.metric_name} is {metric_value}, which {rule.comparison} {rule.threshold}"
                
                # Create alert object
                alert = Alert(
                    database_id=db_id,
                    alert_type=rule.metric_name,
                    severity=rule.severity,
                    message=message,
                    timestamp=datetime.utcnow()
                )
                
                self.db.add(alert)
                generated_alerts.append(alert)
        
        if generated_alerts:
            self.db.commit()
            
        return generated_alerts
    
    def check_recovery(self, db_id: int, metrics: Dict[str, Any]) -> List[Alert]:
        """
        Check if any previously triggered alerts can now be resolved.
        
        Args:
            db_id: Database connection ID
            metrics: Dictionary of collected metrics
            
        Returns:
            List of resolved alerts
        """
        # Get all unresolved alerts for this database
        unresolved_alerts = self.db.query(Alert).filter(
            Alert.database_id == db_id,
            Alert.resolved == False
        ).all()
        
        resolved_alerts = []
        
        for alert in unresolved_alerts:
            # Get the corresponding rule for this alert
            rule = self.db.query(AlertRule).filter(
                AlertRule.database_id == db_id,
                AlertRule.metric_name == alert.alert_type,
                AlertRule.enabled == True
            ).first()
            
            if not rule:
                continue
                
            # Get the metric value if it exists
            if rule.metric_name not in metrics or metrics[rule.metric_name] is None:
                continue
                
            metric_value = metrics[rule.metric_name]
            alert_resolved = False
            
            # Check if threshold is no longer exceeded based on comparison operator
            if rule.comparison == ">":
                alert_resolved = metric_value <= rule.threshold
            elif rule.comparison == "<":
                alert_resolved = metric_value >= rule.threshold
            elif rule.comparison == ">=":
                alert_resolved = metric_value < rule.threshold
            elif rule.comparison == "<=":
                alert_resolved = metric_value > rule.threshold
            elif rule.comparison == "==":
                alert_resolved = metric_value != rule.threshold
            
            if alert_resolved:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                resolved_alerts.append(alert)
        
        if resolved_alerts:
            self.db.commit()
            
        return resolved_alerts