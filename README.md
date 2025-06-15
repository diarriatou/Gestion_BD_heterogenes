# Plateforme de Gestion de Bases de Données Hétérogènes

Une plateforme FastAPI pour la gestion centralisée de bases de données hétérogènes (MySQL, MongoDB, Oracle) avec monitoring, alertes et sauvegardes automatisées.

## 🚀 Fonctionnalités

- **Monitoring en temps réel** des métriques de performance
- **Alertes automatiques** basées sur des seuils configurables
- **Gestion des utilisateurs** avec authentification JWT
- **Sauvegardes automatisées** avec planification
- **Interface REST API** complète
- **Support multi-bases** : MySQL, MongoDB, Oracle

## 📋 Prérequis

- Python 3.8+
- MySQL Server
- MongoDB (optionnel)
- Oracle Database (optionnel)

## 🛠️ Installation

1. **Cloner le repository**
```bash
git clone <repository-url>
cd Gestion_BD_heterogenes
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données**
```bash
python init_database.py
```

5. **Lancer l'application**
```bash
python -m uvicorn app.main:app --reload
```

## ⚙️ Configuration

Créez un fichier `.env` à la racine du projet :

```env
# Configuration de la base de données MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=db_management

# Configuration de l'API
API_SECRET_KEY=your_secret_key_here_change_in_production
API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration du monitoring
METRICS_COLLECTION_INTERVAL=60
MAX_METRICS_HISTORY=100

# Seuils d'alerte par défaut
DEFAULT_CPU_WARNING=70.0
DEFAULT_CPU_CRITICAL=90.0
DEFAULT_MEMORY_WARNING=75.0
DEFAULT_MEMORY_CRITICAL=90.0
```

## 📚 API Documentation

Une fois l'application lancée, accédez à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Endpoints principaux

#### Authentification
- `POST /api/users/token` - Connexion utilisateur
- `GET /api/users/me` - Profil utilisateur actuel

#### Monitoring
- `GET /api/monitoring/databases` - Liste des bases de données
- `POST /api/monitoring/databases` - Ajouter une base de données
- `GET /api/monitoring/metrics` - Métriques collectées
- `GET /api/monitoring/alerts` - Alertes actives

#### Sauvegardes
- `GET /api/backups/schedules` - Plannings de sauvegarde
- `POST /api/backups/schedules` - Créer un planning
- `GET /api/backups/history` - Historique des sauvegardes

## 🧪 Tests

Exécuter les tests unitaires :

```bash
pytest tests/
```

## 📊 Métriques collectées

### MySQL
- Utilisation CPU
- Utilisation mémoire
- Nombre de connexions actives
- Latence des requêtes
- Transactions actives

### MongoDB
- Utilisation mémoire
- Nombre de connexions
- Opérations par seconde
- Statistiques de performance

### Oracle
- Utilisation CPU
- Utilisation mémoire SGA
- Sessions utilisateur actives
- Transactions actives

## 🔔 Système d'alertes

Le système génère automatiquement des alertes basées sur :
- **CPU** : > 70% (warning), > 90% (critical)
- **Mémoire** : > 75% (warning), > 90% (critical)
- **Connexions** : > 100 (warning), > 200 (critical)
- **Latence** : > 1s (warning), > 5s (critical)

## 🔧 Améliorations récentes

- ✅ Configuration centralisée avec classe Settings
- ✅ Gestion robuste des erreurs et logging
- ✅ Pool de connexions SQLAlchemy
- ✅ Validations Pydantic améliorées
- ✅ Tests unitaires
- ✅ Documentation complète
- ✅ Gestion des contextes de base de données

## 🚨 Dépannage

### Problème de connexion MySQL
```bash
# Vérifier que MySQL est démarré
# Windows
net start mysql

# Linux
sudo systemctl start mysql
```

### Erreur de dépendances
```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt
```

### Problème de permissions
```bash
# Vérifier les permissions de l'utilisateur MySQL
GRANT ALL PRIVILEGES ON db_management.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

## 📝 Structure du projet

```
app/
├── main.py              # Point d'entrée FastAPI
├── config.py            # Configuration centralisée
├── database.py          # Gestion des connexions DB
├── dependencies.py      # Dépendances FastAPI
├── modules/
│   ├── monitoring/      # Module de monitoring
│   ├── users/          # Module utilisateurs
│   └── backups/        # Module sauvegardes
└── adapters/           # Adaptateurs de bases de données
tests/                  # Tests unitaires
requirements.txt        # Dépendances Python
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement 