#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def create_database():
    """Créer la base de données si elle n'existe pas"""
    try:
        # Connexion à MySQL sans spécifier de base de données
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Créer la base de données si elle n'existe pas
            db_name = os.getenv("DB_NAME", "db_management")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Base de données '{db_name}' créée ou déjà existante.")
            
            cursor.close()
            connection.close()
            print("Connexion MySQL fermée.")
            
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        print("Assurez-vous que MySQL est démarré et accessible.")

if __name__ == "__main__":
    create_database() 