#!/usr/bin/env python3
"""
Script pour configurer les connexions réelles dans l'application
"""

import os
import json
from datetime import datetime

def create_env_file():
    """Crée un fichier .env avec les configurations de base de données"""
    
    env_content = """# Configuration des bases de données
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=gestion_bd_heterogenes

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=gestion_bd_heterogenes
MONGODB_USERNAME=admin
MONGODB_PASSWORD=password

# Oracle
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_USER=system
ORACLE_PASSWORD=oracle
ORACLE_SERVICE_NAME=XE

# Configuration de l'application
API_SECRET_KEY=your-secret-key-here-change-in-production
API_ALGORITHM=HS256
API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration de la base de données principale (SQLite pour le développement)
DATABASE_URL=sqlite:///./gestion_bd_heterogenes.db

# Configuration du scheduler
SCHEDULER_INTERVAL_MINUTES=60
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Fichier .env créé avec succès")

def create_database_config():
    """Crée un fichier de configuration JSON pour les bases de données"""
    
    config = {
        "databases": {
            "mysql": {
                "name": "MySQL Production",
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "password",
                "database": "gestion_bd_heterogenes",
                "enabled": True
            },
            "mongodb": {
                "name": "MongoDB Production",
                "type": "mongodb",
                "host": "localhost",
                "port": 27017,
                "database": "gestion_bd_heterogenes",
                "username": "admin",
                "password": "password",
                "enabled": True
            },
            "oracle": {
                "name": "Oracle Production",
                "type": "oracle",
                "host": "localhost",
                "port": 1521,
                "user": "system",
                "password": "oracle",
                "service_name": "XE",
                "enabled": True
            }
        },
        "monitoring": {
            "enabled": True,
            "interval_minutes": 60,
            "metrics_retention_days": 30
        },
        "backup": {
            "enabled": True,
            "schedule": "0 2 * * *",  # Tous les jours à 2h du matin
            "retention_days": 7
        }
    }
    
    with open('database_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Fichier database_config.json créé avec succès")

def create_connection_test_script():
    """Crée un script de test des connexions"""
    
    script_content = '''#!/usr/bin/env python3
"""
Script de test des connexions de base de données
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire app au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_connections():
    """Teste toutes les connexions configurées"""
    print("🔍 Test des connexions de base de données...")
    
    # Test MySQL
    try:
        from app.adapters.mysql_adapter import MySQLAdapter
        mysql = MySQLAdapter(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'password'),
            database=os.getenv('MYSQL_DATABASE', 'gestion_bd_heterogenes')
        )
        
        if mysql.connect():
            print("✅ MySQL: Connexion réussie")
            metrics = mysql.get_metrics()
            print(f"   📊 Métriques: {metrics}")
            mysql.disconnect()
        else:
            print("❌ MySQL: Échec de connexion")
    except Exception as e:
        print(f"❌ MySQL: Erreur - {e}")
    
    # Test MongoDB
    try:
        from app.adapters.mongo_adapter import MongoDBAdapter
        mongo = MongoDBAdapter(
            host=os.getenv('MONGODB_HOST', 'localhost'),
            port=int(os.getenv('MONGODB_PORT', 27017)),
            database=os.getenv('MONGODB_DATABASE', 'gestion_bd_heterogenes'),
            username=os.getenv('MONGODB_USERNAME', 'admin'),
            password=os.getenv('MONGODB_PASSWORD', 'password')
        )
        
        if mongo.connect():
            print("✅ MongoDB: Connexion réussie")
            metrics = mongo.get_metrics()
            print(f"   📊 Métriques: {metrics}")
            mongo.disconnect()
        else:
            print("❌ MongoDB: Échec de connexion")
    except Exception as e:
        print(f"❌ MongoDB: Erreur - {e}")
    
    # Test Oracle
    try:
        from app.adapters.oracle_adapter import OracleAdapter
        oracle = OracleAdapter(
            host=os.getenv('ORACLE_HOST', 'localhost'),
            port=int(os.getenv('ORACLE_PORT', 1521)),
            user=os.getenv('ORACLE_USER', 'system'),
            password=os.getenv('ORACLE_PASSWORD', 'oracle'),
            service_name=os.getenv('ORACLE_SERVICE_NAME', 'XE')
        )
        
        if oracle.connect():
            print("✅ Oracle: Connexion réussie")
            metrics = oracle.get_metrics()
            print(f"   📊 Métriques: {metrics}")
            oracle.disconnect()
        else:
            print("❌ Oracle: Échec de connexion")
    except Exception as e:
        print(f"❌ Oracle: Erreur - {e}")

if __name__ == "__main__":
    test_connections()
'''
    
    with open('test_connections.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Script test_connections.py créé avec succès")

def main():
    """Fonction principale"""
    print("🚀 Configuration des connexions de base de données")
    print("=" * 50)
    print(f"⏰ Configuration: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Créer les fichiers de configuration
    create_env_file()
    create_database_config()
    create_connection_test_script()
    
    print("\n" + "=" * 50)
    print("📋 Fichiers créés:")
    print("  ✅ .env - Variables d'environnement")
    print("  ✅ database_config.json - Configuration des bases de données")
    print("  ✅ test_connections.py - Script de test des connexions")
    
    print("\n💡 Prochaines étapes:")
    print("  1. Modifiez le fichier .env avec vos vraies informations de connexion")
    print("  2. Exécutez: python test_connections.py pour tester les connexions")
    print("  3. Exécutez: python -m uvicorn app.main:app --reload pour démarrer l'application")
    
    print("\n⚠️  Important:")
    print("  - Changez les mots de passe par défaut dans .env")
    print("  - Assurez-vous que les bases de données sont en cours d'exécution")
    print("  - Vérifiez que les ports ne sont pas bloqués par le pare-feu")

if __name__ == "__main__":
    main() 