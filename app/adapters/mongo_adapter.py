import pymongo
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

    def backup(self, destination_path):
        """Sauvegarde la base MongoDB en JSON."""
        try:
            import json
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            collections = self.db.list_collection_names()
            backup_data = {}
            
            for collection in collections:
                data = list(self.db[collection].find({}, {"_id": 0}))
                backup_data[collection] = data
            
            with open(destination_path, 'w') as f:
                json.dump(backup_data, f, indent=4)

            return {'status': 'success', 'path': destination_path}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def restore(self, backup_path):
        """Restaure la base MongoDB depuis un fichier JSON."""
        try:
            import json
            if not os.path.exists(backup_path):
                return {'status': 'error', 'message': f"Le fichier {backup_path} n'existe pas"}

            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            for collection, data in backup_data.items():
                self.db[collection].insert_many(data)
            
            return {'status': 'success', 'restored_from': backup_path}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

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
