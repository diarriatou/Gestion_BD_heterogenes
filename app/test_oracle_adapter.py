from adapters.oracle_adapter import OracleAdapter

# Configuration de l'adaptateur
host = "192.168.1.8"  # Remplace par l'IP de ton serveur Oracle
port = 1521
user = "user1"
password = "1234"
service_name = "orcl"

# Initialisation de l'adaptateur
adapter = OracleAdapter(host, port, user, password, service_name)

# Tester la connexion
print("🔄 Tentative de connexion...")
if adapter.connect():
    print("✅ Connexion réussie !")
else:
    print("❌ Échec de la connexion.")
    exit()

# Récupérer la liste des utilisateurs
print("\n📋 Liste des utilisateurs Oracle :")
users = adapter.get_users()
print(users)

# Récupérer les métriques de la base de données
print("\n📊 Récupération des métriques de la base :")
metrics = adapter.get_metrics()
print(metrics)

# Tester la sauvegarde
backup_path = "/chemin/vers/backup.dmp"  # Remplace par un vrai chemin
print("\n💾 Test de la sauvegarde...")
backup_result = adapter.backup(backup_path)
print(backup_result)

# Déconnexion
adapter.disconnect()
print("\n🔌 Déconnecté de la base Oracle.")
