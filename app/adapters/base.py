class DatabaseAdapter:
    """Interface commune pour tous les adaptateurs de bases de données."""
    
    def connect(self):
        """Établit la connexion à la base de données."""
        raise NotImplementedError
    
    def disconnect(self):
        """Ferme la connexion à la base de données."""
        raise NotImplementedError
    
    def get_users(self):
        """Récupère la liste des utilisateurs de la base de données."""
        raise NotImplementedError
    
    def create_user(self, username, password, roles=None):
        """Crée un nouvel utilisateur dans la base de données."""
        raise NotImplementedError
    
    def delete_user(self, username):
        """Supprime un utilisateur de la base de données."""
        raise NotImplementedError
    
    def get_performance_metrics(self):
        """Récupère les métriques de performance de la base de données."""
        raise NotImplementedError
    
    def backup(self, destination_path):
        """Exécute une sauvegarde de la base de données."""
        raise NotImplementedError
    
    def restore(self, backup_path):
        """Restaure une base de données à partir d'une sauvegarde."""
        raise NotImplementedError