import pytest
from oracle_adapter import OracleAdapter

# Configuration de connexion (à adapter selon ton environnement)
HOST = "localhost"
PORT = 1521
USER = "ousmane"
PASSWORD = "oracle"
SERVICE_NAME = "XEPDB1"

@pytest.fixture
def oracle_adapter():
    adapter = OracleAdapter(HOST, PORT, USER, PASSWORD, SERVICE_NAME)
    adapter.connect()
    yield adapter  # Fournit l'instance pour les tests
    adapter.disconnect()

def test_connection(oracle_adapter):
    assert oracle_adapter.connection is not None, "La connexion à Oracle 19c a échoué."

def test_get_users(oracle_adapter):
    users = oracle_adapter.get_users()
    assert isinstance(users, list), "La liste des utilisateurs doit être un tableau."
    assert len(users) > 0, "Il doit y avoir au moins un utilisateur en base."

def test_create_and_delete_user(oracle_adapter):
    username = "pytest_user"
    password = "pytest123"

    # Création de l'utilisateur
    assert oracle_adapter.create_user(username, password), "Échec de la création de l'utilisateur."

    # Vérification de l'existence
    users = oracle_adapter.get_users()
    assert any(u["username"] == username for u in users), "L'utilisateur pytest_user n'a pas été trouvé."

    # Suppression de l'utilisateur
    assert oracle_adapter.delete_user(username), "Échec de la suppression de l'utilisateur."

    # Vérification de la suppression
    users = oracle_adapter.get_users()
    assert not any(u["username"] == username for u in users), "L'utilisateur pytest_user existe toujours après suppression."
