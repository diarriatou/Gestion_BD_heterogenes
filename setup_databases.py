#!/usr/bin/env python3
"""
Script pour configurer et démarrer les bases de données
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def check_mysql_service():
    """Vérifie si MySQL est en cours d'exécution"""
    try:
        result = subprocess.run(['mysql', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_mongodb_service():
    """Vérifie si MongoDB est en cours d'exécution"""
    try:
        result = subprocess.run(['mongod', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_oracle_service():
    """Vérifie si Oracle est en cours d'exécution"""
    try:
        result = subprocess.run(['sqlplus', '-V'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def start_mysql():
    """Démarre MySQL"""
    print("🔧 Démarrage de MySQL...")
    try:
        # Essayer de démarrer le service MySQL
        subprocess.run(['net', 'start', 'MySQL'], 
                      capture_output=True, text=True, timeout=30)
        time.sleep(5)  # Attendre que le service démarre
        return True
    except Exception as e:
        print(f"⚠️  Impossible de démarrer MySQL automatiquement: {e}")
        print("💡 Veuillez démarrer MySQL manuellement")
        return False

def start_mongodb():
    """Démarre MongoDB"""
    print("🔧 Démarrage de MongoDB...")
    try:
        # Créer le répertoire de données MongoDB s'il n'existe pas
        data_dir = "C:\\data\\db"
        os.makedirs(data_dir, exist_ok=True)
        
        # Démarrer MongoDB en arrière-plan
        subprocess.Popen(['mongod', '--dbpath', data_dir], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(5)  # Attendre que MongoDB démarre
        return True
    except Exception as e:
        print(f"⚠️  Impossible de démarrer MongoDB automatiquement: {e}")
        print("💡 Veuillez démarrer MongoDB manuellement")
        return False

def create_mysql_database():
    """Crée la base de données MySQL si elle n'existe pas"""
    print("🔧 Création de la base de données MySQL...")
    try:
        # Connexion à MySQL pour créer la base de données
        create_db_sql = """
        CREATE DATABASE IF NOT EXISTS gestion_bd_heterogenes;
        USE gestion_bd_heterogenes;
        
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            metric_name VARCHAR(100) NOT NULL,
            metric_value FLOAT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Exécuter les commandes SQL
        subprocess.run(['mysql', '-u', 'root', '-p'], 
                      input=create_db_sql, text=True, timeout=30)
        return True
    except Exception as e:
        print(f"⚠️  Impossible de créer la base de données MySQL: {e}")
        return False

def create_mongodb_database():
    """Crée la base de données MongoDB si elle n'existe pas"""
    print("🔧 Création de la base de données MongoDB...")
    try:
        # Script JavaScript pour MongoDB
        mongo_script = """
        use gestion_bd_heterogenes;
        
        // Créer une collection users si elle n'existe pas
        db.createCollection('users');
        
        // Créer une collection metrics si elle n'existe pas
        db.createCollection('metrics');
        
        // Insérer un document de test
        db.users.insertOne({
            username: 'admin',
            email: 'admin@example.com',
            created_at: new Date()
        });
        
        print('Base de données MongoDB créée avec succès');
        """
        
        # Exécuter le script MongoDB
        subprocess.run(['mongo'], input=mongo_script, text=True, timeout=30)
        return True
    except Exception as e:
        print(f"⚠️  Impossible de créer la base de données MongoDB: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Configuration des bases de données")
    print("=" * 50)
    print(f"⏰ Début de la configuration: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier les services
    print("\n🔍 Vérification des services de base de données...")
    
    mysql_available = check_mysql_service()
    mongodb_available = check_mongodb_service()
    oracle_available = check_oracle_service()
    
    print(f"  MySQL: {'✅ Disponible' if mysql_available else '❌ Non disponible'}")
    print(f"  MongoDB: {'✅ Disponible' if mongodb_available else '❌ Non disponible'}")
    print(f"  Oracle: {'✅ Disponible' if oracle_available else '❌ Non disponible'}")
    
    # Démarrer les services si nécessaire
    if not mysql_available:
        print("\n🔧 Tentative de démarrage de MySQL...")
        mysql_available = start_mysql()
    
    if not mongodb_available:
        print("\n🔧 Tentative de démarrage de MongoDB...")
        mongodb_available = start_mongodb()
    
    # Créer les bases de données
    if mysql_available:
        print("\n🔧 Configuration de MySQL...")
        create_mysql_database()
    
    if mongodb_available:
        print("\n🔧 Configuration de MongoDB...")
        create_mongodb_database()
    
    print("\n" + "=" * 50)
    print("📋 Résumé de la configuration:")
    print(f"  MySQL: {'✅ Configuré' if mysql_available else '❌ Non configuré'}")
    print(f"  MongoDB: {'✅ Configuré' if mongodb_available else '❌ Non configuré'}")
    print(f"  Oracle: {'✅ Disponible' if oracle_available else '❌ Non disponible'}")
    
    if mysql_available or mongodb_available:
        print("\n🎉 Configuration terminée!")
        print("💡 Vous pouvez maintenant exécuter: python test_real_connections.py")
    else:
        print("\n💥 Aucune base de données n'a pu être configurée.")
        print("💡 Veuillez installer et configurer manuellement les bases de données.")

if __name__ == "__main__":
    main() 