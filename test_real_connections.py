#!/usr/bin/env python3
"""
Script pour tester les connexions réelles aux bases de données
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire app au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database_config import MYSQL_CONFIG, MONGODB_CONFIG, ORACLE_CONFIG
from app.adapters.mysql_adapter import MySQLAdapter
from app.adapters.mongo_adapter import MongoDBAdapter
from app.adapters.oracle_adapter import OracleAdapter

def test_mysql_connection():
    """Test de connexion MySQL"""
    print("🔍 Test de connexion MySQL...")
    try:
        adapter = MySQLAdapter(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database']
        )
        
        if adapter.connect():
            print("✅ Connexion MySQL réussie!")
            
            # Test des métriques
            metrics = adapter.get_metrics()
            print(f"📊 Métriques MySQL: {metrics}")
            
            # Test de récupération des utilisateurs
            users = adapter.get_users()
            print(f"👥 Utilisateurs MySQL: {len(users)} trouvés")
            
            adapter.disconnect()
            return True
        else:
            print("❌ Échec de connexion MySQL")
            return False
            
    except Exception as e:
        print(f"❌ Erreur MySQL: {e}")
        return False

def test_mongodb_connection():
    """Test de connexion MongoDB"""
    print("\n🔍 Test de connexion MongoDB...")
    try:
        adapter = MongoDBAdapter(
            host=MONGODB_CONFIG['host'],
            port=MONGODB_CONFIG['port'],
            database=MONGODB_CONFIG['database'],
            username=MONGODB_CONFIG['username'],
            password=MONGODB_CONFIG['password']
        )
        
        if adapter.connect():
            print("✅ Connexion MongoDB réussie!")
            
            # Test des métriques
            metrics = adapter.get_metrics()
            print(f"📊 Métriques MongoDB: {metrics}")
            
            # Test de récupération des utilisateurs
            users = adapter.get_users()
            print(f"👥 Utilisateurs MongoDB: {len(users)} trouvés")
            
            adapter.disconnect()
            return True
        else:
            print("❌ Échec de connexion MongoDB")
            return False
            
    except Exception as e:
        print(f"❌ Erreur MongoDB: {e}")
        return False

def test_oracle_connection():
    """Test de connexion Oracle"""
    print("\n🔍 Test de connexion Oracle...")
    try:
        adapter = OracleAdapter(
            host=ORACLE_CONFIG['host'],
            port=ORACLE_CONFIG['port'],
            user=ORACLE_CONFIG['user'],
            password=ORACLE_CONFIG['password'],
            service_name=ORACLE_CONFIG['service_name']
        )
        
        if adapter.connect():
            print("✅ Connexion Oracle réussie!")
            
            # Test des métriques
            metrics = adapter.get_metrics()
            print(f"📊 Métriques Oracle: {metrics}")
            
            # Test de récupération des utilisateurs
            users = adapter.get_users()
            print(f"👥 Utilisateurs Oracle: {len(users)} trouvés")
            
            adapter.disconnect()
            return True
        else:
            print("❌ Échec de connexion Oracle")
            return False
            
    except Exception as e:
        print(f"❌ Erreur Oracle: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test des connexions de base de données")
    print("=" * 50)
    print(f"⏰ Début des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'mysql': test_mysql_connection(),
        'mongodb': test_mongodb_connection(),
        'oracle': test_oracle_connection()
    }
    
    print("\n" + "=" * 50)
    print("📋 Résumé des tests:")
    for db, success in results.items():
        status = "✅ Réussi" if success else "❌ Échec"
        print(f"  {db.upper()}: {status}")
    
    successful_connections = sum(results.values())
    total_connections = len(results)
    
    print(f"\n🎯 Résultat global: {successful_connections}/{total_connections} connexions réussies")
    
    if successful_connections == total_connections:
        print("🎉 Toutes les connexions sont opérationnelles!")
    elif successful_connections > 0:
        print("⚠️  Certaines connexions fonctionnent, d'autres échouent")
    else:
        print("💥 Aucune connexion ne fonctionne. Vérifiez vos configurations.")

if __name__ == "__main__":
    main() 