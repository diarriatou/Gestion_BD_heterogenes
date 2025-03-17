import pytest
import mongomock
from adapters.mongo_adapter import MongoDBAdapter  # Assure-toi que le chemin d'importation est correct

@pytest.fixture
def mock_mongo_adapter():
    """Fixture pour simuler un adaptateur MongoDB avec mongomock."""
    adapter = MongoDBAdapter("localhost", 27017, "user", "password", "test")
    adapter.client = mongomock.MongoClient()  # Simule MongoDB en mémoire
    adapter.db = adapter.client["test_db"]
    return adapter

def test_connect(mock_mongo_adapter):
    """Teste la connexion simulée à MongoDB."""
    assert mock_mongo_adapter.connect() is True

def test_backup(mock_mongo_adapter, tmp_path):
    """Teste la sauvegarde des données MongoDB en JSON."""
    # Insérer des données fictives
    mock_mongo_adapter.db["users"].insert_one({"name": "Alice", "age": 30})
    
    backup_path = tmp_path / "backup.json"
    result = mock_mongo_adapter.backup(str(backup_path))

    assert result["status"] == "success"
    assert backup_path.exists()

def test_restore(mock_mongo_adapter, tmp_path):
    """Teste la restauration des données MongoDB à partir d'un fichier JSON."""
    backup_path = tmp_path / "backup.json"

    # Créer un fichier JSON de test
    backup_data = {
        "users": [{"name": "Bob", "age": 25}]
    }
    backup_path.write_text(str(backup_data))

    result = mock_mongo_adapter.restore(str(backup_path))

    assert result["status"] == "success"
    assert mock_mongo_adapter.db["users"].find_one({"name": "Bob"}) is not None

def test_create_user(mock_mongo_adapter):
    """Teste la création d'un utilisateur MongoDB."""
    result = mock_mongo_adapter.create_user("test_user", "secure_password")
    assert result["status"] == "success"

def test_delete_user(mock_mongo_adapter):
    """Teste la suppression d'un utilisateur MongoDB."""
    mock_mongo_adapter.create_user("test_user", "secure_password")
    result = mock_mongo_adapter.delete_user("test_user")
    assert result["status"] == "success"

def test_get_metrics(mock_mongo_adapter):
    """Teste la récupération des métriques de la base MongoDB."""
    mock_mongo_adapter.db["users"].insert_many([{"name": "Alice"}, {"name": "Bob"}])
    result = mock_mongo_adapter.get_metrics()

    assert result["status"] == "success"
    assert result["collection_count"] > 0
