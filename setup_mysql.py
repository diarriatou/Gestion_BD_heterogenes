#!/usr/bin/env python3
"""
Script pour configurer MySQL pour les tests
"""

import subprocess
import sys
import os

def setup_mysql():
    """Configure MySQL pour les tests"""
    print("🔧 Configuration de MySQL pour les tests...")
    
    # Script SQL pour configurer MySQL
    setup_sql = """
    -- Créer la base de données si elle n'existe pas
    CREATE DATABASE IF NOT EXISTS gestion_bd_heterogenes;
    
    -- Utiliser la base de données
    USE gestion_bd_heterogenes;
    
    -- Créer un utilisateur de test sans mot de passe (pour les tests uniquement)
    CREATE USER IF NOT EXISTS 'testuser'@'localhost' IDENTIFIED BY '';
    GRANT ALL PRIVILEGES ON gestion_bd_heterogenes.* TO 'testuser'@'localhost';
    FLUSH PRIVILEGES;
    
    -- Créer les tables de test
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
    
    -- Insérer des données de test
    INSERT IGNORE INTO users (username, email) VALUES 
    ('admin', 'admin@example.com'),
    ('user1', 'user1@example.com'),
    ('user2', 'user2@example.com');
    
    INSERT IGNORE INTO metrics (metric_name, metric_value) VALUES 
    ('cpu_usage', 45.5),
    ('memory_usage', 67.2),
    ('disk_usage', 23.8);
    
    SELECT 'MySQL configuration completed successfully' as status;
    """
    
    try:
        # Essayer d'abord avec root sans mot de passe
        print("  Tentative de connexion avec root (sans mot de passe)...")
        result = subprocess.run(['mysql', '-u', 'root'], 
                              input=setup_sql, text=True, 
                              capture_output=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Configuration MySQL réussie avec root")
            return True
        else:
            print(f"  Échec avec root: {result.stderr}")
            
            # Essayer avec root et mot de passe
            print("  Tentative de connexion avec root (mot de passe: root)...")
            result = subprocess.run(['mysql', '-u', 'root', '-proot'], 
                                  input=setup_sql, text=True, 
                                  capture_output=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Configuration MySQL réussie avec root/root")
                return True
            else:
                print(f"  Échec avec root/root: {result.stderr}")
                
                # Essayer avec root et mot de passe vide
                print("  Tentative de connexion avec root (mot de passe vide)...")
                result = subprocess.run(['mysql', '-u', 'root', '-p'], 
                                      input='\n' + setup_sql, text=True, 
                                      capture_output=True, timeout=30)
                
                if result.returncode == 0:
                    print("✅ Configuration MySQL réussie avec root (mot de passe vide)")
                    return True
                else:
                    print(f"  Échec avec root (mot de passe vide): {result.stderr}")
                    return False
                    
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors de la configuration MySQL")
        return False
    except FileNotFoundError:
        print("❌ MySQL n'est pas installé ou n'est pas dans le PATH")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la configuration MySQL: {e}")
        return False

def update_env_file():
    """Met à jour le fichier .env avec les bonnes configurations"""
    print("🔧 Mise à jour du fichier .env...")
    
    env_content = """# Configuration des bases de données
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=testuser
MYSQL_PASSWORD=
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
    
    print("✅ Fichier .env mis à jour")

def main():
    """Fonction principale"""
    print("🚀 Configuration de MySQL pour les tests")
    print("=" * 50)
    
    if setup_mysql():
        update_env_file()
        print("\n✅ Configuration MySQL terminée!")
        print("💡 Vous pouvez maintenant tester les connexions avec: python test_connections.py")
    else:
        print("\n❌ Échec de la configuration MySQL")
        print("💡 Veuillez configurer MySQL manuellement ou vérifier l'installation")

if __name__ == "__main__":
    main() 