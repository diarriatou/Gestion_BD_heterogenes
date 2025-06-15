import pytest
from unittest.mock import Mock, patch
import os
import sys

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def mock_database_connections():
    """Mock automatique des connexions de base de données pour tous les tests"""
    with patch('app.database.engine') as mock_engine:
        with patch('app.database.SessionLocal') as mock_session:
            mock_session.return_value = Mock()
            yield mock_session

@pytest.fixture
def mock_mysql_connection():
    """Mock pour les connexions MySQL"""
    with patch('app.modules.monitoring.collector.mysql.connector.connect') as mock_connect:
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        yield mock_connection, mock_cursor

@pytest.fixture
def mock_mongodb_connection():
    """Mock pour les connexions MongoDB"""
    with patch('app.modules.monitoring.collector.pymongo.MongoClient') as mock_client:
        mock_mongo_client = Mock()
        mock_db = Mock()
        mock_client.return_value = mock_mongo_client
        mock_mongo_client.__getitem__ = Mock(return_value=mock_db)
        yield mock_mongo_client, mock_db

@pytest.fixture
def mock_oracle_connection():
    """Mock pour les connexions Oracle"""
    with patch('app.modules.monitoring.collector.oracledb.connect') as mock_connect:
        with patch('app.modules.monitoring.collector.oracledb.makedsn') as mock_makedsn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_connection
            mock_connection.cursor.return_value = mock_cursor
            mock_makedsn.return_value = "test_dsn"
            yield mock_connection, mock_cursor

@pytest.fixture
def sample_metrics_data():
    """Données de métriques d'exemple pour les tests"""
    return {
        "cpu_usage": 25.5,
        "memory_usage": 60.2,
        "disk_usage": 45.0,
        "connections_count": 10,
        "query_latency": 0.5,
        "active_transactions": 5,
        "timestamp": "2024-01-01T12:00:00"
    }

@pytest.fixture
def sample_database_connection():
    """Connexion de base de données d'exemple pour les tests"""
    return {
        "id": 1,
        "name": "Test Database",
        "host": "localhost",
        "port": 3306,
        "db_type": "mysql",
        "username": "test_user",
        "password": "test_pass",
        "database_name": "test_db",
        "is_active": True
    } 