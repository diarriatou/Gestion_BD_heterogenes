import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Intercepteur pour ajouter le token d'authentification
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Service d'authentification
export const authService = {
  login: async (credentials) => {
    const response = await API.post("/api/users/login", credentials);
    return response.data;
  },
  register: async (userData) => {
    const response = await API.post("/api/users/register", userData);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem("token");
  },
};

// Service de monitoring
export const monitoringService = {
  getMetrics: async () => {
    const response = await API.get("/api/monitoring/metrics");
    return response.data;
  },
  getDatabaseStatus: async () => {
    const response = await API.get("/api/monitoring/status");
    return response.data;
  },
  getPerformanceMetrics: async () => {
    const response = await API.get("/api/monitoring/performance");
    return response.data;
  },
};

// Service de sauvegardes
export const backupService = {
  createBackup: async (databaseType, config) => {
    const response = await API.post("/api/backups/create", {
      database_type: databaseType,
      config,
    });
    return response.data;
  },
  getBackups: async () => {
    const response = await API.get("/api/backups/list");
    return response.data;
  },
  restoreBackup: async (backupId) => {
    const response = await API.post(`/api/backups/restore/${backupId}`);
    return response.data;
  },
  deleteBackup: async (backupId) => {
    const response = await API.delete(`/api/backups/${backupId}`);
    return response.data;
  },
};

// Service de gestion des utilisateurs
export const userService = {
  getUsers: async () => {
    const response = await API.get("/api/users");
    return response.data;
  },
  createUser: async (userData) => {
    const response = await API.post("/api/users", userData);
    return response.data;
  },
  updateUser: async (userId, userData) => {
    const response = await API.put(`/api/users/${userId}`, userData);
    return response.data;
  },
  deleteUser: async (userId) => {
    const response = await API.delete(`/api/users/${userId}`);
    return response.data;
  },
};

// Service de configuration des bases de données
export const databaseService = {
  getDatabases: async () => {
    const response = await API.get("/api/databases");
    return response.data;
  },
  testConnection: async (config) => {
    const response = await API.post("/api/databases/test", config);
    return response.data;
  },
  addDatabase: async (config) => {
    const response = await API.post("/api/databases", config);
    return response.data;
  },
  updateDatabase: async (dbId, config) => {
    const response = await API.put(`/api/databases/${dbId}`, config);
    return response.data;
  },
  deleteDatabase: async (dbId) => {
    const response = await API.delete(`/api/databases/${dbId}`);
    return response.data;
  },
};

export default API; 