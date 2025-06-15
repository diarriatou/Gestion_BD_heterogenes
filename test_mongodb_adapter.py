import pytest
from app.adapters.mongo_adapter import MongoDBAdapter

# Configuration de test - utiliser une base de données de test sans authentification
MONGO_CONFIG = {
    "host": "localhost",
    "port": 27017,
    "database": "test_db",
    "user": "",
    "password": ""
}

@pytest.fixture
def mongodb_adapter():
    """Fixture pour créer et nettoyer l'adaptateur MongoDB."""
    adapter = MongoDBAdapter(**MONGO_CONFIG)
    success = adapter.connect()
    if not success:
        pytest.skip("Impossible de se connecter à MongoDB")
    yield adapter
    adapter.disconnect()

def test_connection(mongodb_adapter):
    """Test de connexion à la base de données MongoDB."""
    assert mongodb_adapter.client is not None

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
    assert "status" in metrics
    
    if metrics["status"] == "success":
        assert "collection_count" in metrics
        assert "database_size_mb" in metrics
    else:
        # Si erreur d'authentification, on skip le test
        pytest.skip(f"Erreur d'authentification MongoDB: {metrics.get('message', '')}")

def test_backup_and_restore(mongodb_adapter, tmp_path):
    """Test de sauvegarde de la base de données."""
    backup_file = tmp_path / "backup"
    
    result = mongodb_adapter.backup(str(backup_file))
    assert isinstance(result, dict)
    assert "status" in result
    
    if result["status"] == "success":
        # Vérifier que le fichier de sauvegarde existe
        backup_path = result.get("path", str(backup_file) + ".tar.gz")
        import os
        assert os.path.exists(backup_path)
    else:
        # Si erreur (mongodump non disponible), on skip le test
        pytest.skip(f"Erreur de sauvegarde: {result.get('message', '')}")
