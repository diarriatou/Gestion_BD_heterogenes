import pymongo
import os
import subprocess
from datetime import datetime
from .base import DatabaseAdapter

class MongoDBAdapter(DatabaseAdapter):
    """Adaptateur pour MongoDB."""
    
    def __init__(self, host, port, user, password, database):
        self.uri = f"mongodb://{user}:{password}@{host}:{port}/{database}"
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = pymongo.MongoClient(self.uri)
            self.db = self.client.get_default_database()
            return True
        except pymongo.errors.PyMongoError as e:
            print(f"Erreur de connexion MongoDB: {e}")
            return False

    def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None

    def create_user(self, username, password):
        """Crée un utilisateur MongoDB."""
        try:
            self.db.command("createUser", username, pwd=password, roles=[{"role": "readWrite", "db": self.db.name}])
            return {'status': 'success', 'message': f'Utilisateur {username} créé avec succès'}
        except pymongo.errors.PyMongoError as e:
            return {'status': 'error', 'message': str(e)}

    def delete_user(self, username):
        """Supprime un utilisateur MongoDB."""
        try:
            self.db.command("dropUser", username)
            return {'status': 'success', 'message': f'Utilisateur {username} supprimé avec succès'}
        except pymongo.errors.PyMongoError as e:
            return {'status': 'error', 'message': str(e)}

    def get_metrics(self):
        """Récupère les métriques de la base MongoDB."""
        try:
            user_count = self.db.command("usersInfo")["users"]
            collection_count = len(self.db.list_collection_names())
            
            db_stats = self.db.command("dbStats")
            db_size = db_stats["dataSize"] / 1024 / 1024  # Taille en MB
            
            return {
                'status': 'success',
                'user_count': len(user_count),
                'collection_count': collection_count,
                'database_size_mb': db_size
            }
        except pymongo.errors.PyMongoError as e:
            return {'status': 'error', 'message': str(e)}

def insert(self, collection_name, data):
    try:
        result = self.db[collection_name].insert_one(data)
        return {"status": "success", "inserted_id": result.inserted_id}
    except pymongo.errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}

def find(self, collection_name, query):
    try:
        data = list(self.db[collection_name].find(query))
        return {"status": "success", "data": data}
    except pymongo.errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}

def delete(self, collection_name, query):
    try:
        result = self.db[collection_name].delete_one(query)
        return {"status": "success", "deleted_count": result.deleted_count}
    except pymongo.errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}


def backup(self, destination_path, backup_type="full"):
    """Sauvegarde la base MongoDB à chaud avec mongodump."""
    try:
        # Créer le répertoire de destination
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Construire la commande mongodump
        db_name = self.uri.split("/")[-1]
        
        # Extraire les composants de l'URI
        parts = self.uri.split("@")
        auth = parts[0].replace("mongodb://", "")
        host_part = parts[1].split("/")[0]
        
        cmd = [
            'mongodump',
            f'--uri={self.uri}',
            f'--out={destination_path}',
            '--oplog'  # Option clé pour la sauvegarde à chaud
        ]
        
        # Exécuter mongodump
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        # Compresser le répertoire de sortie
        compressed_path = f"{destination_path}.tar.gz"
        subprocess.run(['tar', '-czf', compressed_path, destination_path], check=True)
        
        # Nettoyer le répertoire original
        subprocess.run(['rm', '-rf', destination_path], check=True)
        
        return {
            'status': 'success',
            'path': compressed_path,
            'database': db_name,
            'size': os.path.getsize(compressed_path),
            'timestamp': datetime.now().isoformat()
        }
    except subprocess.SubprocessError as e:
        return {
            'status': 'error',
            'message': str(e)
        }