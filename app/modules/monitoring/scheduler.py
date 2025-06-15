from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
import logging
from app.database import SessionLocal, get_db_context
from app.modules.monitoring.models import DatabaseConnection
from app.modules.monitoring.collector import get_collector
from app.modules.monitoring.analyzer import MetricAnalyzer
from app.config import settings
from datetime import datetime
import app.modules.monitoring.models as models

logger = logging.getLogger(__name__)

def collect_metrics_job():
    """Scheduled job to collect metrics from all databases"""
    logger.info("Starting metrics collection job")
    
    with get_db_context() as db:
        try:
            # Get all active database connections
            connections = db.query(DatabaseConnection).filter(DatabaseConnection.is_active == True).all()
            logger.info(f"Found {len(connections)} active database connections")
            
            for connection in connections:
                try:
                    logger.info(f"Collecting metrics for database: {connection.name}")
                    
                    # Create collector for specific database type
                    connection_params = {
                        "host": connection.host,
                        "port": connection.port,
                        "username": connection.username,
                        "password": connection.password,
                        "database": ("information_schema" if connection.db_type.lower() == "mysql" 
                            else "admin" if connection.db_type.lower() == "mongodb"
                            else ""),
                        "service_name": "XE" if connection.db_type.lower() == "oracle" else "orcl"
                    }
                    
                    collector = get_collector(connection.db_type, connection_params)
                    metrics_data = collector.collect_metrics()
                    
                    # Check if there was an error collecting metrics
                    if "error" in metrics_data:
                        logger.error(f"Error collecting metrics for {connection.name}: {metrics_data['error']}")
                        continue
                    
                    # Store metrics in database
                    metric = models.Metric(
                        database_id=connection.id,
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
                    
                    # Analyze metrics for alerts
                    analyzer = MetricAnalyzer(connection_id=connection.id, db_type=connection.db_type)
                    alerts = analyzer.analyze_metrics(metrics_data)
                    
                    if alerts:
                        logger.info(f"Generated {len(alerts)} alerts for database {connection.name}")
                        # Store alerts in database
                        for alert_data in alerts:
                            alert = models.Alert(
                                database_id=connection.id,
                                alert_type=alert_data["alert_type"],
                                severity=alert_data["severity"],
                                message=alert_data["message"],
                                timestamp=alert_data["timestamp"]
                            )
                            db.add(alert)
                        db.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing database {connection.name}: {str(e)}")
                    db.rollback()
                    
        except Exception as e:
            logger.error(f"Error in metrics collection job: {str(e)}")
            db.rollback()

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler(
        job_defaults={
            'coalesce': True,  # Combine multiple pending executions
            'max_instances': 1,  # Only one instance of each job
            'misfire_grace_time': 300  # 5 minutes grace time
        }
    )
    
    # Add job to collect metrics
    scheduler.add_job(
        collect_metrics_job,
        IntervalTrigger(minutes=settings.METRICS_COLLECTION_INTERVAL),
        id="collect_metrics_job",
        replace_existing=True,
        name="Database Metrics Collection"
    )
    
    try:
        scheduler.start()
        logger.info(f"Started metrics collection scheduler (interval: {settings.METRICS_COLLECTION_INTERVAL} minutes)")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        raise
    
    return scheduler