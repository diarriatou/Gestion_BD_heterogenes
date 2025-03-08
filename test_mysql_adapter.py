import pytest
from app.adapters.mysql_adapter import MySQLAdapter

# Configuration de test
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "test_db"
}

@pytest.fixture
def mysql_adapter():
    """Fixture pour créer et nettoyer l'adaptateur MySQL."""
    adapter = MySQLAdapter(**MYSQL_CONFIG)
    adapter.connect()
    yield adapter
    adapter.disconnect()

def test_connection(mysql_adapter):
    """Test de connexion à la base de données MySQL."""
    assert mysql_adapter.connection is not None

def test_create_and_delete_user(mysql_adapter):
    """Test de création et suppression d'un utilisateur."""
    username = "test_user"
    password = "test_password"

    assert mysql_adapter.create_user(username, password, ["read_only"]) == True
    users = mysql_adapter.get_users()
    assert any(user["username"] == username for user in users)

    assert mysql_adapter.delete_user(username) == True
    users = mysql_adapter.get_users()
    assert not any(user["username"] == username for user in users)

def test_get_performance_metrics(mysql_adapter):
    """Test de récupération des métriques MySQL."""
    metrics = mysql_adapter.get_performance_metrics()
    assert isinstance(metrics, dict)
    assert "total_connections" in metrics
    assert "total_queries" in metrics

def test_backup_and_restore(mysql_adapter, tmp_path):
    """Test de sauvegarde et restauration de la base de données."""
    backup_file = tmp_path / "backup.sql"

    result = mysql_adapter.backup(str(backup_file))
    print(result) 
    assert result["status"] == "success"
    assert backup_file.exists()

    restore_result = mysql_adapter.restore(str(backup_file))
    assert restore_result["status"] == "success"
