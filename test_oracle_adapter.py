import pytest
from app.adapters.oracle_adapter import OracleAdapter

@pytest.fixture
def oracle_adapter():
    """Fixture pour initialiser l'adaptateur Oracle avec les bonnes configurations."""
    adapter = OracleAdapter(host="localhost", port=1521, user="diarra_user", password="passer", service_name="unitydb")
    yield adapter
    adapter.disconnect()

def test_connection(oracle_adapter):
    """Test de connexion à Oracle."""
    assert oracle_adapter.connect() == True

def test_create_and_delete_user(oracle_adapter):
    """Test de création et suppression d'un utilisateur."""
    username = "test_user"
    password = "TestPass123"
    
    result = oracle_adapter.create_user(username, password)
    assert result["status"] == "success"
    
    result = oracle_adapter.delete_user(username)
    assert result["status"] == "success"

def test_get_performance_metrics(oracle_adapter):
    """Test de récupération des métriques de performance."""
    metrics = oracle_adapter.get_performance_metrics()
    assert metrics and "cpu_usage" in metrics and "sessions" in metrics

def test_backup_and_restore(oracle_adapter, tmp_path):
    """Test de sauvegarde et restauration de la base de données."""
    backup_file = tmp_path / "oracle_backup.dmp"
    
    result = oracle_adapter.backup(str(backup_file))
    assert result["status"] == "success", f"Backup failed: {result['message']}"
    
    result = oracle_adapter.restore(str(backup_file))
    assert result["status"] == "success", f"Restore failed: {result['message']}"
