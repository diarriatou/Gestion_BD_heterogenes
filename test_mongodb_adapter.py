import pytest
from app.adapters.mongo_adapter import MongoDBAdapter

# Configuration de test
MONGO_CONFIG = {
    "host": "localhost",
    "port": 27017,
    "database": "admin",
    "user": "root" ,
    "password": "password"
}

@pytest.fixture
def mongodb_adapter():
    """Fixture pour créer et nettoyer l'adaptateur MongoDB."""
    adapter = MongoDBAdapter(**MONGO_CONFIG)
    adapter.connect()
    yield adapter
    adapter.disconnect()

def test_connection(mongodb_adapter):
    """Test de connexion à la base de données MongoDB."""
    assert mongodb_adapter.connection is not None

def test_insert_and_delete(mongodb_adapter):
    """Test d'insertion et suppression d'un document."""
    test_data = {"nom": "Test", "valeur": 42}
    insert_result = mongodb_adapter.insert("test_collection", test_data)
    assert "status" in insert_result and insert_result["status"] == "success"
    inserted_id = insert_result["inserted_id"]
    
    find_result = mongodb_adapter.find("test_collection", {"_id": inserted_id})
    assert "status" in find_result and find_result["status"] == "success"
    assert len(find_result["data"]) > 0
    
    delete_result = mongodb_adapter.delete("test_collection", {"_id": inserted_id})
    assert "status" in delete_result and delete_result["status"] == "success"

def test_get_metrics(mongodb_adapter):
    """Test de récupération des métriques MongoDB."""
    metrics = mongodb_adapter.get_metrics()
    assert isinstance(metrics, dict)
    assert "collection_count" in metrics
    assert "database_size_mb" in metrics

def test_backup_and_restore(mongodb_adapter, tmp_path):
    """Test de sauvegarde et restauration de la base de données."""
    backup_file = tmp_path / "backup.bson"
    
    result = mongodb_adapter.backup(str(backup_file))
    assert result["status"] == "success"
    assert backup_file.exists()
    
    restore_result = mongodb_adapter.restore(str(backup_file))
    assert restore_result["status"] == "success"
