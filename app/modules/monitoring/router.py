from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.modules.monitoring import schemas
from app.modules.monitoring.models import DatabaseConnection, Metric, Alert, AlertRule
from app.database import get_db
from app.modules.monitoring.collector import get_collector
from app.modules.monitoring.analyzer import MetricAnalyzer

router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"]
)
@router.post("/connections", response_model=schemas.DatabaseConnectionResponse)
def create_database_connection(connection: schemas.DatabaseConnectionCreate, db: Session = Depends(get_db)):
    """Register a new database connection for monitoring"""
    db_connection = DatabaseConnection(
        name=connection.name,
        host=connection.host,
        port=connection.port,
        db_type=connection.db_type,
        username=connection.username,
        password=connection.password,
        # Ajoutez d'autres champs si nécessaire
    )
    
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    
    return db_connection
@router.post("/metrics/collect/{db_id}", response_model=schemas.MetricResponse)
def collect_metrics(db_id: int, db: Session = Depends(get_db)):
    """Manually trigger metrics collection for a specific database"""
    # Get database connection info
    db_connection = db.query(DatabaseConnection).filter(DatabaseConnection.id == db_id).first()
    if not db_connection:
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    # Create collector for specific database type
    connection_params = {
        "host": db_connection.host,
        "port": db_connection.port,
        "username": db_connection.username,
        "password": db_connection.password,
        # Additional parameters depending on db type
        "database": "information_schema" if db_connection.db_type.lower() == "mysql" else "",
        "service_name": "" if db_connection.db_type.lower() != "oracle" else "XE"  # Default service name
    }
    
    collector = get_collector(db_connection.db_type, connection_params)
    metrics_data = collector.collect_metrics()
    
    # Store metrics in database
    metric = Metric(
        database_id=db_id,
        cpu_usage=metrics_data.get("cpu_usage"),
        memory_usage=metrics_data.get("memory_usage"),
        disk_usage=metrics_data.get("disk_usage"),
        connections_count=metrics_data.get("connections_count"),
        query_latency=metrics_data.get("query_latency"),
        active_transactions=metrics_data.get("active_transactions"),
        timestamp=metrics_data.get("timestamp", datetime.utcnow())
    )
    
    db.add(metric)
    db.commit()
    db.refresh(metric)
    
    # Analyze metrics and generate alerts
    analyzer = MetricAnalyzer(db)
    alerts = analyzer.analyze_metrics(db_id, metrics_data)
    resolved = analyzer.check_recovery(db_id, metrics_data)
    
    return metric

@router.get("/metrics/{db_id}", response_model=List[schemas.MetricResponse])
def get_metrics(
    db_id: int, 
    start_time: Optional[datetime] = None, 
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get metrics for a specific database with optional time range filtering"""
    query = db.query(Metric).filter(Metric.database_id == db_id)
    
    if start_time:
        query = query.filter(Metric.timestamp >= start_time)
    else:
        # Default to last 24 hours
        query = query.filter(Metric.timestamp >= datetime.utcnow() - timedelta(days=1))
        
    if end_time:
        query = query.filter(Metric.timestamp <= end_time)
        
    return query.order_by(Metric.timestamp.desc()).limit(limit).all()

@router.get("/alerts", response_model=List[schemas.AlertResponse])
def get_alerts(
    resolved: Optional[bool] = None,
    db_id: Optional[int] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get alerts with optional filtering"""
    query = db.query(Alert)
    
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)
        
    if db_id:
        query = query.filter(Alert.database_id == db_id)
        
    if severity:
        query = query.filter(Alert.severity == severity)
        
    return query.order_by(Alert.timestamp.desc()).limit(limit).all()

@router.post("/alerts/rules", response_model=schemas.AlertRuleResponse)
def create_alert_rule(rule: schemas.AlertRuleCreate, db: Session = Depends(get_db)):
    """Create a new alert rule"""
    # Check if database exists
    db_connection = db.query(DatabaseConnection).filter(DatabaseConnection.id == rule.database_id).first()
    if not db_connection:
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    # Validate comparison operator
    valid_operators = [">", "<", ">=", "<=", "=="]
    if rule.comparison not in valid_operators:
        raise HTTPException(status_code=400, detail=f"Invalid comparison operator. Must be one of {valid_operators}")
    
    # Validate severity
    valid_severities = ["Low", "Medium", "High", "Critical"]
    if rule.severity not in valid_severities:
        raise HTTPException(status_code=400, detail=f"Invalid severity. Must be one of {valid_severities}")
    
    # Create alert rule
    alert_rule = AlertRule(
        database_id=rule.database_id,
        metric_name=rule.metric_name,
        threshold=rule.threshold,
        comparison=rule.comparison,
        severity=rule.severity,
        enabled=rule.enabled
    )
    
    db.add(alert_rule)
    db.commit()
    db.refresh(alert_rule)
    
    return alert_rule

@router.put("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Manually resolve an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.resolved:
        raise HTTPException(status_code=400, detail="Alert is already resolved")
    
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return {"message": "Alert resolved successfully"}

@router.get("/summary/{db_id}")
def get_monitoring_summary(db_id: int, db: Session = Depends(get_db)):
    """Get a summary of the database's current status"""
    # Get database connection
    db_connection = db.query(DatabaseConnection).filter(DatabaseConnection.id == db_id).first()
    if not db_connection:
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    # Get latest metric
    latest_metric = db.query(Metric).filter(
        Metric.database_id == db_id
    ).order_by(Metric.timestamp.desc()).first()
    
    # Get active alerts count
    active_alerts = db.query(Alert).filter(
        Alert.database_id == db_id,
        Alert.resolved == False
    ).count()
    
    # Get alerts by severity
    critical_alerts = db.query(Alert).filter(
        Alert.database_id == db_id,
        Alert.resolved == False,
        Alert.severity == "Critical"
    ).count()
    
    high_alerts = db.query(Alert).filter(
        Alert.database_id == db_id,
        Alert.resolved == False,
        Alert.severity == "High"
    ).count()
    
    # Generate status based on alerts
    status = "Healthy"
    if critical_alerts > 0:
        status = "Critical"
    elif high_alerts > 0:
        status = "Warning"
    
    return {
        "database_name": db_connection.name,
        "status": status,
        "latest_metrics": latest_metric,
        "active_alerts": active_alerts,
        "critical_alerts": critical_alerts,
        "high_alerts": high_alerts,
        "last_updated": latest_metric.timestamp if latest_metric else None
    }