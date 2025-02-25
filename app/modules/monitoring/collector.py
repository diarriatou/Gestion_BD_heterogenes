import time
from datetime import datetime , timezone
from pymongo import MongoClient
import mysql.connector
import cx_Oracle

class DatabaseCollector:
    def __init__(self, db_config, storage_config):
        self.db_config = db_config  # Infos de connexion pour la base surveillée
        self.storage_config = storage_config  # Infos pour MySQL central

    def collect_metrics(self):
        metrics = {}

        if self.db_config['db_type'] == 'MongoDB':
            metrics = self.collect_mongo_metrics()
        elif self.db_config['db_type'] == 'MySQL':
            metrics = self.collect_mysql_metrics()
        elif self.db_config['db_type'] == 'Oracle':
            metrics = self.collect_oracle_metrics()

        return metrics

    def collect_mongo_metrics(self):
        client = MongoClient(self.db_config['host'], self.db_config['port'])
        db = client[self.db_config['db_name']]
        stats = db.command("dbStats")
        database_size = stats['dataSize'] / (1024 * 1024)  # Convertir en Mo
        
        return {
            'db_name': self.db_config['db_name'],
            'database_size_mb': database_size,
            'slow_queries': 3,
            'cpu_usage': 35.2,
            'memory_usage': 65.4,
            'disk_usage': 80.1,
            'active_connections': 120,
            'uptime': 86400,
            'last_updated': datetime.now(timezone.utc)
        }

    def collect_mysql_metrics(self):
        conn = mysql.connector.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password="",
            database=self.db_config['db_name']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT table_schema AS db_name, SUM(data_length + index_length) / 1024 / 1024 AS database_size_mb FROM information_schema.tables WHERE table_schema = %s GROUP BY table_schema", (self.db_config['db_name'],))
        result = cursor.fetchone()
        database_size = result[1] if result else 0

        return {
            'db_name': self.db_config['db_name'],
            'database_size_mb': database_size,
            'slow_queries': 3,
            'cpu_usage': 35.2,
            'memory_usage': 65.4,
            'disk_usage': 80.1,
            'active_connections': 120,
            'uptime': 86400,
            'last_updated': datetime.now(timezone.utc)
        }

    def collect_oracle_metrics(self):
        conn = cx_Oracle.connect(
            user=self.db_config['system'],
            password=self.db_config['ipHone6#'],
            dsn=self.db_config['localhost/unitydb']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(bytes) / 1024 / 1024 AS database_size_mb FROM dba_data_files")
        result = cursor.fetchone()
        database_size = result[0] if result else 0

        return {
            'db_name': self.db_config['db_name'],
            'database_size_mb': database_size,
            'slow_queries': 3,
            'cpu_usage': 35.2,
            'memory_usage': 65.4,
            'disk_usage': 80.1,
            'active_connections': 120,
            'uptime': 86400,
            'last_updated': datetime.now(timezone.utc)
        }
    
    def store_metrics(self, metrics):
        try:
            conn = mysql.connector.connect(
                host=self.storage_config['host'],
                user=self.storage_config['user'],
                password=self.storage_config['password'],
                database=self.storage_config['db_name']
            )
            cursor = conn.cursor()

            query = """
            INSERT INTO metrics (db_name, database_size_mb, slow_queries, cpu_usage, 
                                 memory_usage, disk_usage, active_connections, uptime, last_updated) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                metrics['db_name'],
                metrics['database_size_mb'],
                metrics['slow_queries'],
                metrics['cpu_usage'],
                metrics['memory_usage'],
                metrics['disk_usage'],
                metrics['active_connections'],
                metrics['uptime'],
                metrics['last_updated']
            )

            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()

            print("✅ Données stockées avec succès dans db_management !")

        except Exception as e:
            print("❌ Erreur lors de l'insertion :", e)

# Exemple de config pour la base surveillée et la base centrale
db_config = {
    'db_type': 'MySQL',
    'host': 'localhost',
    'user': 'root',
    'password': "",
    'db_name': 'db_management'
}

storage_config = {
    'host': 'localhost',
    'user': 'root',
    'password': "",
    'db_name': 'db_management'
}

collector = DatabaseCollector(db_config, storage_config)
metrics = collector.collect_metrics()
collector.store_metrics(metrics)
