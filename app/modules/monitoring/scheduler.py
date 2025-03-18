from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
import logging
from app.database import SessionLocal
from app.modules.monitoring.models import DatabaseConnection
from app.modules.monitoring.collector import get_collector
from app.modules.monitoring.analyzer import MetricAnalyzer
from datetime import datetime
import app.modules.monitoring.models as models

logger = logging.getLogger(__name__)

# def collect_metrics_job():
    
#     """Scheduled job to collect metrics from all databases"""
#     db = SessionLocal()
#     try:
#         # Get all active database connections
#         connections = db.query(DatabaseConnection).all()
        
#         for connection in connections:
#             try:
#                 # Create collector for specific database type
#                 connection_params = {
#                     "host": connection.host,
#                     "port": connection.port,
#                     "username": connection.username,
#                     "password": connection.password,
#                     # Additional parameters depending on db type
#                     "database": "information_schema" if connection.db_type.lower() == "mysql" else "",
#                     "service_name": "" if connection.db_type.lower() != "oracle" else "XE"  # Default service name
#                 }
                
#                 collector = get_collector(connection.db_type, connection_params)
#                 metrics_data = collector.collect_metrics()
                
#                 # Store metrics in database
#                 metric = models.Metric(
#                     database_id=connection.id,
#                     cpu_usage=metrics_data.get("cpu_usage"),
#                     memory_usage=metrics_data.get("memory_usage"),
#                     disk_usage=metrics_data.get("disk_usage"),
#                     connections_count=metrics_data.get("connections_count"),
#                     query_latency=metrics_data.get("query_latency"),
#                     active_transactions=metrics_data.get("active_transactions"),
#                     timestamp=metrics_data.get("timestamp", datetime.utcnow())
#                 )
                
#                 db.add(metric)
#                 db.commit()
                
#                 # Analyze metrics and generate alerts
#                 # analyzer = MetricAnalyzer(connection_id=1, db_type="mysql")
#                 analyzer = MetricAnalyzer(connection_id=connection.id, db_type=connection.db_type)
#                 # alerts = analyzer.analyze_metrics(connection.id, metrics_data)
#                 alerts = analyzer.analyze_metrics(metrics_data)
#                 resolved = analyzer.check_recovery(connection.id, metrics_data)
                
#                 if alerts:
#                     logger.info(f"Generated {len(alerts)} alerts for database {connection.name}")
                
#                 if resolved:
#                     logger.info(f"Resolved {len(resolved)} alerts for database {connection.name}")
                
#             except Exception as e:
#                 logger.error(f"Error collecting metrics for database {connection.name}: {str(e)}")
#                 db.rollback()
    
#     except Exception as e:
#         logger.error(f"Error in metrics collection job: {str(e)}")
    
#     finally:
#         db.close()

def collect_metrics_job():
    """Scheduled job to collect metrics from all databases"""
    db = SessionLocal()
    try:
        # Get all active database connections
        connections = db.query(DatabaseConnection).all()
       
        for connection in connections:
            try:
                # Create collector for specific database type
                connection_params = {
                    "host": connection.host,
                    "port": connection.port,
                    "username": connection.username,
                    "password": connection.password,
                    # Additional parameters depending on db type
                    "database": ("information_schema" if connection.db_type.lower() == "mysql" 
                        else "admin" if connection.db_type.lower() == "mongodb"  # Utiliser "admin" ou une autre DB valide
                        else ""),
                    "service_name": "orcl" if connection.db_type.lower() != "oracle" else "XE"  # Default service name
                }
               
                collector = get_collector(connection.db_type, connection_params)
                metrics_data = collector.collect_metrics()
               
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
               
                # Corriger cette partie - Utiliser l'ID de la connexion réelle et passer le type de DB
                analyzer = MetricAnalyzer(connection_id=connection.id, db_type=connection.db_type)
                
                # Ne passer que metrics_data à analyze_metrics comme défini dans la classe MetricAnalyzer
                alerts = analyzer.analyze_metrics(metrics_data)
                
                # Pour la méthode check_recovery, vous devez l'ajouter à la classe MetricAnalyzer
                # Si cette méthode n'existe pas, commentez ou supprimez la ligne suivante
                # resolved = analyzer.check_recovery(metrics_data)
                
                if alerts:
                    logger.info(f"Generated {len(alerts)} alerts for database {connection.name}")
               
                # Commentez ou supprimez cette partie si check_recovery n'existe pas
                # if resolved:
                #     logger.info(f"Resolved {len(resolved)} alerts for database {connection.name}")
               
            except Exception as e:
                logger.error(f"Error collecting metrics for database {connection.name}: {str(e)}")
                db.rollback()
   
    except Exception as e:
        logger.error(f"Error in metrics collection job: {str(e)}")
   
    finally:
        db.close()
def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Add job to collect metrics every minute
    scheduler.add_job(
        collect_metrics_job,
        IntervalTrigger(minutes=60),
        id="collect_metrics_job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Started metrics collection scheduler")
    
    return scheduler