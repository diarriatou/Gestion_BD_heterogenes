from app.modules.monitoring.collector import DatabaseCollector

# Configuration de test (adapte selon tes bases)
db_config = {
    'db_type': 'MySQL',  # ou 'MySQL', 'Oracle'
    'host': 'localhost',
    'port': 3306,
    'db_name': 'teste_db',
    'user': 'root',  # Pour MySQL et Oracle
    'password': ''  # Pour MySQL et Oracle
}

# Initialiser et exécuter la collecte
collector = DatabaseCollector(db_config)
metrics = collector.collect_metrics()

# Afficher les résultats
print("📊 Métriques collectées :")
for key, value in metrics.items():
    print(f"{key}: {value}")
