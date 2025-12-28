
"""
Templates for generating frontend code files.
"""

HTTP_CLIENT_TEMPLATE = '''import axios from 'axios';
import { ENV } from '../config/env';

const httpClient = axios.create({
  baseURL: ENV.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: ENV.API_TIMEOUT || 10000,
});

httpClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

httpClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
       // Handle unauthorized
    }
    return Promise.reject(error);
  }
);

export default httpClient;
'''

ENV_TS_TEMPLATE = '''export const ENV = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  IS_DEV: import.meta.env.DEV,
  IS_PROD: import.meta.env.PROD,
  API_TIMEOUT: Number(import.meta.env.VITE_API_TIMEOUT) || 10000,
};
'''

ENDPOINTS_TS_TEMPLATE = '''export const ENDPOINTS = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        ME: '/auth/me',
    },
    // Add feature specific endpoints here
} as const;
'''

ROUTES_TS_TEMPLATE = '''export const ROUTES = {
    HOME: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    DASHBOARD: '/dashboard',
    NOT_FOUND: '*',
} as const;
'''

APP_TSX_TEMPLATE = '''import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ROUTES } from './constants/routes';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
           <Route path={ROUTES.HOME} element={<div>Home</div>} />
           <Route path={ROUTES.LOGIN} element={<div>Login</div>} />
           <Route path={ROUTES.DASHBOARD} element={<div>Dashboard</div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
'''
