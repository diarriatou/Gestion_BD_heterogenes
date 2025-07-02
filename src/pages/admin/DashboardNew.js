import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Users, 
  HardDrive, 
  Activity, 
  AlertTriangle, 
  CheckCircle,
  Loader,
  RefreshCw
} from 'lucide-react';
import { monitoringService, backupService, userService } from '../../services/api';

export default function DashboardNew() {
  const [metrics, setMetrics] = useState(null);
  const [backups, setBackups] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Récupérer les données en parallèle
      const [metricsData, backupsData, usersData] = await Promise.all([
        monitoringService.getMetrics(),
        backupService.getBackups(),
        userService.getUsers()
      ]);
      
      setMetrics(metricsData);
      setBackups(backupsData);
      setUsers(usersData);
    } catch (err) {
      setError('Erreur lors du chargement des données');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Chargement du tableau de bord...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="flex items-center mx-auto px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
        <p className="text-gray-600 mt-2">Vue d'ensemble de vos bases de données</p>
      </div>

      {/* Métriques principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Database className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Bases de données</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics?.database_count || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Users className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Utilisateurs</p>
              <p className="text-2xl font-bold text-gray-900">
                {users?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <HardDrive className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Sauvegardes</p>
              <p className="text-2xl font-bold text-gray-900">
                {backups?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Performance</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics?.performance_score || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Statut des bases de données */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Statut des bases</h3>
          <div className="space-y-3">
            {metrics?.databases?.map((db, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 ${
                    db.status === 'online' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className="font-medium">{db.name}</span>
                </div>
                <span className={`text-sm ${
                  db.status === 'online' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {db.status === 'online' ? 'En ligne' : 'Hors ligne'}
                </span>
              </div>
            )) || (
              <p className="text-gray-500">Aucune base de données configurée</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sauvegardes récentes</h3>
          <div className="space-y-3">
            {backups?.slice(0, 5).map((backup, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{backup.database_name}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(backup.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center">
                  {backup.status === 'completed' ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertTriangle className="h-5 w-5 text-yellow-500" />
                  )}
                </div>
              </div>
            )) || (
              <p className="text-gray-500">Aucune sauvegarde récente</p>
            )}
          </div>
        </div>
      </div>

      {/* Actions rapides */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
            <Database className="h-4 w-4 mr-2" />
            Ajouter une base
          </button>
          <button className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700">
            <HardDrive className="h-4 w-4 mr-2" />
            Créer une sauvegarde
          </button>
          <button className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700">
            <Activity className="h-4 w-4 mr-2" />
            Voir les métriques
          </button>
        </div>
      </div>
    </div>
  );
} 