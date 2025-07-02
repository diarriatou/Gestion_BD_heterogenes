from app.modules.monitoring.collector import get_collector

# Configuration de test
db_config = {
    'host': 'localhost',
    'port': 3306,
    'username': 'root',  # Pour MySQL et Oracle
    'password': '',  # Pour MySQL et Oracle
    'database': 'teste_db'  # Pour MySQL et MongoDB
}

# Initialiser et exécuter la collecte
collector = get_collector('mysql', db_config)
metrics = collector.collect_metrics()

# Afficher les résultats
print("📊 Métriques collectées :")
for key, value in metrics.items():
    print(f"{key}: {value}")
