import time
import logging
import schedule
from app.modules.monitoring.collector import DatabaseCollector

# Configuration du logging
logging.basicConfig(
    filename="collector.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration des bases de données à surveiller
databases = [
    {
        'db_type': 'MongoDB',
        'host': 'localhost',
        'port': 27017,
        'db_name': 'teste_db'
    },
    {
        'db_type': 'MySQL',
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'db_name': 'teste_db'
    },
    {
        'db_type': 'Oracle',
        'host': 'localhost/unitydb',
        'user': 'system',
        'password': 'ipHone6#'
    }
]

def collect_and_store():
    """ Fonction pour collecter et stocker les métriques """
    for db_config in databases:
        try:
            collector = DatabaseCollector(db_config)
            metrics = collector.collect_metrics()
            collector.store_metrics(metrics)
            logging.info(f"Métriques collectées avec succès pour {db_config['db_type']}")
        except Exception as e:
            logging.error(f"Erreur lors de la collecte pour {db_config['db_type']}: {e}")

# Planifier l'exécution toutes les 5 minutes
schedule.every(5).minutes.do(collect_and_store)

if __name__ == "__main__":
    logging.info("Lancement du collecteur automatique...")
    while True:
        schedule.run_pending()
        time.sleep(1)
