
import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\XPS\Downloads\instantclient-basic-windows.x64-23.7.0.25.01\instantclient_23_7")  # Mets ton vrai chemin

import pytest

# Paramètres de connexion (modifie selon ton setup)
DB_USER = "diarra"
DB_PASSWORD = "passer123"
DB_DSN = " 192.168.3.131:1521/orcl"
conn = cx_Oracle.connect(DB_USER, DB_PASSWORD, DB_DSN)
@pytest.fixture
def oracle_connection():
    """Fixture pour établir et fermer la connexion"""
    conn = cx_Oracle.connect(DB_USER, DB_PASSWORD, DB_DSN)
    yield conn
    conn.close()

def test_connection_is_alive(oracle_connection):
    """Vérifie que la connexion est toujours active après l'ouverture."""
    assert oracle_connection.ping() is None

def test_insert_update_delete(oracle_connection):
    """Test d'insertion, mise à jour et suppression de données."""
    cursor = oracle_connection.cursor()

    try:
        # Création de la table
        cursor.execute("CREATE TABLE test_data (id NUMBER PRIMARY KEY, name VARCHAR2(50))")
        oracle_connection.commit()

        # Insertion de données
        cursor.execute("INSERT INTO test_data (id, name) VALUES (1, 'Alice')")
        cursor.execute("INSERT INTO test_data (id, name) VALUES (2, 'Bob')")
        oracle_connection.commit()

        cursor.execute("SELECT COUNT(*) FROM test_data")
        assert cursor.fetchone()[0] == 2

        # Mise à jour
        cursor.execute("UPDATE test_data SET name = 'Charlie' WHERE id = 1")
        oracle_connection.commit()

        cursor.execute("SELECT name FROM test_data WHERE id = 1")
        assert cursor.fetchone()[0] == "Charlie"

        # Suppression
        cursor.execute("DELETE FROM test_data WHERE id = 2")
        oracle_connection.commit()

        cursor.execute("SELECT COUNT(*) FROM test_data")
        assert cursor.fetchone()[0] == 1

        # Suppression de la table
        cursor.execute("DROP TABLE test_data")
        oracle_connection.commit()

    except cx_Oracle.DatabaseError as e:
        pytest.fail(f"Erreur SQL: {e}")