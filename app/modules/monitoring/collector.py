import mysql.connector
import pymongo
import oracledb
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class BaseCollector:
    def collect_metrics(self) -> Dict[str, Any]:
        """Base method to collect metrics"""
        raise NotImplementedError("Subclasses must implement this method")

class MySQLCollector(BaseCollector):
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        
    def connect(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.database
        )
    
    def collect_metrics(self) -> Dict[str, Any]:
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get CPU and memory usage
            cursor.execute("SHOW GLOBAL STATUS")
            status_rows = cursor.fetchall()
            status = {row['Variable_name']: row['Value'] for row in status_rows}
            
            # Get connections count
            cursor.execute("SELECT COUNT(*) as count FROM information_schema.processlist")
            connections = cursor.fetchone()['count']
            
            # Get query latency (avg)
            cursor.execute("SELECT AVG(QUERY_TIME) as avg_latency FROM mysql.slow_log WHERE START_TIME > DATE_SUB(NOW(), INTERVAL 5 MINUTE)")
            latency_row = cursor.fetchone()
            latency = latency_row['avg_latency'] if latency_row and latency_row['avg_latency'] else 0
            
            cursor.close()
            connection.close()
            
            return {
                "cpu_usage": float(status.get('CPU_USAGE', 0)),
                "memory_usage": float(status.get('MEMORY_USAGE', 0)),
                "disk_usage": None,  # Requires additional queries
                "connections_count": connections,
                "query_latency": float(latency),
                "active_transactions": int(status.get('ACTIVE_TRANSACTIONS', 0)),
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error collecting MySQL metrics: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow()
            }

class MongoDBCollector(BaseCollector):
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        
    def connect(self):
        return pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
    
    def collect_metrics(self) -> Dict[str, Any]:
        try:
            client = self.connect()
            db = client[self.database]
            
            # Get server status
            server_status = db.command("serverStatus")
            
            # Extract metrics
            connections = server_status.get("connections", {})
            mem_info = server_status.get("mem", {})
            opcounters = server_status.get("opcounters", {})
            
            client.close()
            
            return {
                "cpu_usage": None,  # MongoDB doesn't provide CPU directly
                "memory_usage": mem_info.get("resident", 0),
                "disk_usage": None,  # Requires additional queries
                "connections_count": connections.get("current", 0),
                "query_latency": None,  # Requires profiling
                "active_transactions": opcounters.get("query", 0) + opcounters.get("insert", 0) + opcounters.get("update", 0) + opcounters.get("delete", 0),
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error collecting MongoDB metrics: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow()
            }

class OracleCollector(BaseCollector):
    def __init__(self, host: str, port: int, username: str, password: str, service_name: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.service_name = service_name
        
    def connect(self):
        dsn = f"{self.host}:{self.port}/{self.service_name}"
        return oracledb.connect(user=self.username, password=self.password, dsn=dsn)
    
    def collect_metrics(self) -> Dict[str, Any]:
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get CPU usage
            cursor.execute("SELECT value FROM v$sysmetric WHERE metric_name = 'CPU Usage Per Sec' AND group_id = 2")
            cpu_row = cursor.fetchone()
            cpu_usage = float(cpu_row[0]) if cpu_row else None
            
            # Get memory usage
            cursor.execute("SELECT round(sum(bytes)/1024/1024,2) FROM v$sgastat")
            memory_row = cursor.fetchone()
            memory_usage = float(memory_row[0]) if memory_row else None
            
            # Get connections count
            cursor.execute("SELECT count(*) FROM v$session WHERE type = 'USER'")
            connection_row = cursor.fetchone()
            connections = int(connection_row[0]) if connection_row else None
            
            # Get active transactions
            cursor.execute("SELECT count(*) FROM v$transaction")
            tx_row = cursor.fetchone()
            transactions = int(tx_row[0]) if tx_row else None
            
            cursor.close()
            connection.close()
            
            return {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": None,  # Requires additional queries
                "connections_count": connections,
                "query_latency": None,  # Requires additional configuration
                "active_transactions": transactions,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error collecting Oracle metrics: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow()
            }

def get_collector(db_type: str, connection_params: Dict[str, Any]) -> BaseCollector:
    """Factory function to get the appropriate collector"""
    if db_type.lower() == "mysql":
        return MySQLCollector(
            host=connection_params["host"],
            port=connection_params["port"],
            username=connection_params["username"],
            password=connection_params["password"],
            database=connection_params.get("database", "")
        )
    elif db_type.lower() == "mongodb":
        return MongoDBCollector(
            host=connection_params["host"],
            port=connection_params["port"],
            username=connection_params["username"],
            password=connection_params["password"],
            database=connection_params.get("database", "")
        )
    elif db_type.lower() == "oracle":
        return OracleCollector(
            host=connection_params["host"],
            port=connection_params["port"],
            username=connection_params["username"],
            password=connection_params["password"],
            service_name=connection_params.get("service_name", "")
        )
    else:
        raise ValueError(f"Unsupported database type: {db_type}")