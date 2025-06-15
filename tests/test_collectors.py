import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.modules.monitoring.collector import MySQLCollector, MongoDBCollector, OracleCollector

class TestMySQLCollector:
    @patch('app.modules.monitoring.collector.MySQLConnectionPool')
    @patch('app.modules.monitoring.collector.mysql.connector.connect')
    def test_collect_metrics_success(self, mock_connect, mock_pool):
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'Variable_name': 'CPU_USAGE', 'Value': '25.5'},
            {'Variable_name': 'MEMORY_USAGE', 'Value': '60.2'},
            {'Variable_name': 'ACTIVE_TRANSACTIONS', 'Value': '5'}
        ]
        mock_cursor.fetchone.side_effect = [
            {'count': 10},
            {'avg_latency': 0.5}
        ]
        # Mock du pool pour retourner le mock de connexion
        mock_pool_instance = Mock()
        mock_pool_instance.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_pool_instance
        collector = MySQLCollector(
            host="localhost",
            port=3306,
            username="test_user",
            password="test_pass",
            database="test_db"
        )
        result = collector.collect_metrics()
        assert result['cpu_usage'] == 25.5
        assert result['memory_usage'] == 60.2
        assert result['connections_count'] == 10
        assert result['query_latency'] == 0.5
        assert result['active_transactions'] == 5
        assert 'timestamp' in result
        assert 'error' not in result

    @patch('app.modules.monitoring.collector.MySQLConnectionPool')
    @patch('app.modules.monitoring.collector.mysql.connector.connect')
    def test_collect_metrics_connection_error(self, mock_connect, mock_pool):
        # Mock du pool pour lever une exception sur get_connection
        mock_pool_instance = Mock()
        mock_pool_instance.get_connection.side_effect = Exception("Connection failed")
        mock_pool.return_value = mock_pool_instance
        collector = MySQLCollector(
            host="localhost",
            port=3306,
            username="test_user",
            password="test_pass",
            database="test_db"
        )
        result = collector.collect_metrics()
        assert 'error' in result
        assert 'Connection failed' in result['error']
        assert 'timestamp' in result

class TestMongoDBCollector:
    @patch('app.modules.monitoring.collector.pymongo.MongoClient')
    def test_collect_metrics_success(self, mock_client):
        collector = MongoDBCollector(
            host="localhost",
            port=27017,
            username="test_user",
            password="test_pass",
            database="test_db"
        )
        mock_mongo_client = MagicMock()
        mock_db = MagicMock()
        mock_client.return_value = mock_mongo_client
        mock_mongo_client.__getitem__.return_value = mock_db
        mock_db.command.return_value = {
            "connections": {"current": 15},
            "mem": {"resident": 1024},
            "opcounters": {
                "query": 100,
                "insert": 50,
                "update": 25,
                "delete": 10
            }
        }
        result = collector.collect_metrics()
        assert result['memory_usage'] == 1024
        assert result['connections_count'] == 15
        assert result['active_transactions'] == 185
        assert result['cpu_usage'] is None
        assert 'timestamp' in result
        assert 'error' not in result

    @patch('app.modules.monitoring.collector.pymongo.MongoClient')
    def test_collect_metrics_connection_error(self, mock_client):
        collector = MongoDBCollector(
            host="localhost",
            port=27017,
            username="test_user",
            password="test_pass",
            database="test_db"
        )
        mock_client.side_effect = Exception("MongoDB connection failed")
        result = collector.collect_metrics()
        assert 'error' in result
        assert 'MongoDB connection failed' in result['error']
        assert 'timestamp' in result

class TestOracleCollector:
    @patch('app.modules.monitoring.collector.oracledb.connect')
    @patch('app.modules.monitoring.collector.oracledb.makedsn')
    def test_collect_metrics_success(self, mock_makedsn, mock_connect):
        collector = OracleCollector(
            host="localhost",
            port=1521,
            username="test_user",
            password="test_pass",
            service_name="XE"
        )
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_makedsn.return_value = "test_dsn"
        mock_cursor.fetchone.side_effect = [
            [15.5],
            [2048.0],
            [20],
            [3]
        ]
        result = collector.collect_metrics()
        assert result['cpu_usage'] == 15.5
        assert result['memory_usage'] == 2048.0
        assert result['connections_count'] == 20
        assert result['active_transactions'] == 3
        assert 'timestamp' in result
        assert 'error' not in result

    @patch('app.modules.monitoring.collector.oracledb.connect')
    @patch('app.modules.monitoring.collector.oracledb.makedsn')
    def test_collect_metrics_connection_error(self, mock_makedsn, mock_connect):
        collector = OracleCollector(
            host="localhost",
            port=1521,
            username="test_user",
            password="test_pass",
            service_name="XE"
        )
        mock_connect.side_effect = Exception("Oracle connection failed")
        mock_makedsn.return_value = "test_dsn"
        result = collector.collect_metrics()
        assert 'error' in result
        assert 'Oracle connection failed' in result['error']
        assert 'timestamp' in result

# Tests pour la fonction factory
class TestCollectorFactory:
    @patch('app.modules.monitoring.collector.MySQLCollector')
    def test_get_mysql_collector(self, mock_mysql_collector):
        from app.modules.monitoring.collector import get_collector
        connection_params = {
            "host": "localhost",
            "port": 3306,
            "username": "test_user",
            "password": "test_pass",
            "database": "test_db"
        }
        collector = get_collector("mysql", connection_params)
        mock_mysql_collector.assert_called_once_with(**connection_params)

    @patch('app.modules.monitoring.collector.MongoDBCollector')
    def test_get_mongodb_collector(self, mock_mongodb_collector):
        from app.modules.monitoring.collector import get_collector
        connection_params = {
            "host": "localhost",
            "port": 27017,
            "username": "test_user",
            "password": "test_pass",
            "database": "test_db"
        }
        collector = get_collector("mongodb", connection_params)
        mock_mongodb_collector.assert_called_once_with(**connection_params)

    @patch('app.modules.monitoring.collector.OracleCollector')
    def test_get_oracle_collector(self, mock_oracle_collector):
        from app.modules.monitoring.collector import get_collector
        connection_params = {
            "host": "localhost",
            "port": 1521,
            "username": "test_user",
            "password": "test_pass",
            "service_name": "XE"
        }
        collector = get_collector("oracle", connection_params)
        mock_oracle_collector.assert_called_once_with(**connection_params)

    def test_get_collector_invalid_type(self):
        from app.modules.monitoring.collector import get_collector
        connection_params = {
            "host": "localhost",
            "port": 5432,
            "username": "test_user",
            "password": "test_pass"
        }
        with pytest.raises(ValueError, match="Unsupported database type"):
            get_collector("postgresql", connection_params)

if __name__ == "__main__":
    pytest.main([__file__])