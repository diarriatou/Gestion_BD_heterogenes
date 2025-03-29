import pymysql
import subprocess
import os
from datetime import datetime
from .base import DatabaseAdapter

class MySQLAdapter(DatabaseAdapter):
    """Adaptateur pour les bases de données MySQL."""
    
    # Objectif : stocker la configuration de la base de données et gérer la connexion à MySQL.
    def __init__(self, host, port, user, password, database):
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None
    
    def connect(self):
        """Établit la connexion à la base de données MySQL."""
        try:
            
            self.connection = pymysql.connect(**self.config)
            return True
        except pymysql.Error as e:
            print(f"Erreur de connexion à MySQL: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion à la base de données MySQL."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_users(self):
        """Récupère la liste des utilisateurs MySQL."""

        # verifier si la connexion est établie
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                # execution de la requête
                cursor.execute("SELECT User, Host FROM mysql.user")
                users = cursor.fetchall()
                # retourner les résultats sous forme de liste de dictionnaires
                return [{"username": user[0], "host": user[1]} for user in users]
        except pymysql.Error as e:
            print(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []

    def create_user(self, username, password, roles=None):
        """Crée un nouvel utilisateur MySQL avec les rôles spécifiés."""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                # Création de l'utilisateur
                cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
                
                # Attribution des privilèges selon les rôles
                if roles:
                    for role in roles:
                        if role == 'admin':
                            cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@'%' WITH GRANT OPTION")
                        elif role == 'read_only':
                            cursor.execute(f"GRANT SELECT ON *.* TO '{username}'@'%'")
                        elif role == 'backup_operator':
                            cursor.execute(f"GRANT SELECT, LOCK TABLES, SHOW VIEW ON *.* TO '{username}'@'%'")
                

            # valide les changements
                cursor.execute("FLUSH PRIVILEGES")
                self.connection.commit()
                return True
        except pymysql.Error as e:
            print(f"Erreur lors de la création de l'utilisateur: {e}")
            return False
    
    def delete_user(self, username):
        """Supprime un utilisateur MySQL."""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DROP USER '{username}'@'%'")
                cursor.execute("FLUSH PRIVILEGES")
                self.connection.commit()
                return True
        except pymysql.Error as e:
            print(f"Erreur lors de la suppression de l'utilisateur: {e}")
            return False
    
    def get_performance_metrics(self):
        """Récupère les métriques de performance MySQL."""
        if not self.connection:
            self.connect()
        
        metrics = {}
        try:
            with self.connection.cursor() as cursor:
                # Métriques de connexions
                cursor.execute("SHOW STATUS LIKE 'Connections'")
                result = cursor.fetchone()
                if result:
                    metrics['total_connections'] = int(result[1])
                
                # Utilisation de la mémoire
                cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_bytes_data'")
                result = cursor.fetchone()
                if result:
                    metrics['buffer_usage_bytes'] = int(result[1])
                
                # Nombre de requêtes
                cursor.execute("SHOW STATUS LIKE 'Queries'")
                result = cursor.fetchone()
                if result:
                    metrics['total_queries'] = int(result[1])
                
                # Temps de fonctionnement
                cursor.execute("SHOW STATUS LIKE 'Uptime'")
                result = cursor.fetchone()
                if result:
                    metrics['uptime_seconds'] = int(result[1])
                
                return metrics
        except pymysql.Error as e:
            print(f"Erreur lors de la récupération des métriques: {e}")
            return metrics
    
    def backup(self, destination_path, backup_type="full"):
        """
        Exécute une sauvegarde à chaud de la base de données MySQL.
        
        Args:
            destination_path: Chemin où enregistrer la sauvegarde
            backup_type: Type de sauvegarde ('full', 'incremental', 'differential')
        
        Returns:
            dict: Résultat de l'opération de sauvegarde
        """
        try:
        # Création du répertoire de destination si nécessaire
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Construction de la commande mysqldump avec options pour sauvegarde à chaud
            cmd = [
            'mysqldump',
            f'--host={self.config["host"]}',
            f'--port={self.config["port"]}',
            f'--user={self.config["user"]}',
            f'--password={self.config["password"]}',
            '--add-drop-database',
            '--single-transaction',  # Garantit la cohérence des données pour InnoDB sans verrouiller les tables
            '--flush-logs',          # Vide les logs binaires pour permettre une restauration point-in-time
            '--master-data=2',       # Inclut la position du binlog sous forme de commentaire
            '--triggers',            # Inclut les triggers
            '--routines',            # Inclut les procédures stockées et fonctions
            '--events',              # Inclut les événements programmés
            '--skip-lock-tables',    # Évite de verrouiller les tables (utilisé avec single-transaction)
            '--databases', self.config['database']
        ]
        
        # Si c'est une sauvegarde incrémentielle, utilisez les binlogs
            if backup_type == "incremental":
            # Enregistrez la position actuelle du binlog pour une utilisation ultérieure
                binlog_info = self._get_binlog_position()
                metadata_path = f"{destination_path}.metadata"
            with open(metadata_path, 'w') as meta_file:
                meta_file.write(f"BINLOG_FILE={binlog_info['file']}\n")
                meta_file.write(f"BINLOG_POS={binlog_info['position']}\n")
                meta_file.write(f"BACKUP_TYPE={backup_type}\n")
        
        # Exécution de la commande et redirection de la sortie vers le fichier
            with open(destination_path, 'w') as f:
                process = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        
        # Compresser le fichier pour économiser de l'espace
            compressed_path = f"{destination_path}.gz"
            subprocess.run(['gzip', '-f', destination_path], check=True)
        
            return {
            'status': 'success',
            'path': compressed_path,
            'database': self.config['database'],
            'type': backup_type,
            'size': os.path.getsize(compressed_path),
            'timestamp': datetime.now().isoformat()
        }
        except (subprocess.SubprocessError, OSError) as e:
            return {
            'status': 'error',
            'message': str(e)
        }

def _get_binlog_position(self):
    """Récupère la position actuelle du binlog pour les sauvegardes incrémentielles."""
    if not self.connection:
        self.connect()
    
    try:
        with self.connection.cursor() as cursor:
            cursor.execute("SHOW MASTER STATUS")
            result = cursor.fetchone()
            if result:
                return {
                    'file': result[0],
                    'position': result[1]
                }
            return None
    except pymysql.Error as e:
        print(f"Erreur lors de la récupération de la position du binlog: {e}")
        return None

def restore(self, backup_path, point_in_time=None):
    """
    Restaure une base de données MySQL à partir d'une sauvegarde.
    
    Args:
        backup_path: Chemin du fichier de sauvegarde
        point_in_time: Pour les restaurations point-in-time (datetime)
    
    Returns:
        dict: Résultat de l'opération de restauration
    """
    try:
        # Vérification que le fichier existe
        if not os.path.exists(backup_path):
            if os.path.exists(f"{backup_path}.gz"):
                # Décompresser le fichier
                subprocess.run(['gunzip', '-f', f"{backup_path}.gz"], check=True)
            else:
                return {'status': 'error', 'message': f"Le fichier de sauvegarde {backup_path} n'existe pas"}
        
        # Construction de la commande mysql
        cmd = [
            'mysql',
            f'--host={self.config["host"]}',
            f'--port={self.config["port"]}',
            f'--user={self.config["user"]}',
            f'--password={self.config["password"]}'
        ]
        
        # Exécution de la commande avec le contenu du fichier en entrée
        with open(backup_path, 'r') as f:
            process = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, check=True)
        
        # Si une restauration point-in-time est demandée
        if point_in_time and os.path.exists(f"{backup_path}.metadata"):
            with open(f"{backup_path}.metadata", 'r') as meta_file:
                metadata = {}
                for line in meta_file:
                    key, value = line.strip().split('=', 1)
                    metadata[key] = value
            
            # Restauration à partir des binlogs jusqu'au point-in-time spécifié
            if 'BINLOG_FILE' in metadata and 'BINLOG_POS' in metadata:
                self._apply_binlogs(metadata['BINLOG_FILE'], 
                                   metadata['BINLOG_POS'],
                                   point_in_time)
        
        return {
            'status': 'success',
            'database': self.config['database'],
            'restored_from': backup_path,
            'point_in_time': point_in_time.isoformat() if point_in_time else None
        }
    except (subprocess.SubprocessError, OSError) as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def _apply_binlogs(self, binlog_file, binlog_pos, point_in_time):
    """Applique les binlogs pour une restauration point-in-time."""
    # Convertir le datetime en format mysql
    time_str = point_in_time.strftime('%Y-%m-%d %H:%M:%S')
    
    cmd = [
        'mysqlbinlog',
        f'--host={self.config["host"]}',
        f'--user={self.config["user"]}',
        f'--password={self.config["password"]}',
        f'--start-position={binlog_pos}',
        f'--stop-datetime="{time_str}"',
        binlog_file
    ]
    
    # Rediriger la sortie vers mysql
    mysqlbinlog_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    mysql_cmd = [
        'mysql',
        f'--host={self.config["host"]}',
        f'--user={self.config["user"]}',
        f'--password={self.config["password"]}',
        self.config['database']
    ]
    subprocess.run(mysql_cmd, stdin=mysqlbinlog_process.stdout, check=True)
    mysqlbinlog_process.stdout.close()