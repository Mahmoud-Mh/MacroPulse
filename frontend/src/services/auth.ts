import axiosInstance from './axios';

const API_URL = '/auth';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await axiosInstance.post(`${API_URL}/token/`, credentials);
      if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
      }
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.error || 'Login failed');
      }
      throw error;
    }
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await axiosInstance.post(`${API_URL}/register/`, data);
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.error || 'Registration failed');
      }
      throw error;
    }
  },

  async refreshToken(): Promise<{ access: string }> {
    try {
      const refresh = localStorage.getItem('refresh_token');
      if (!refresh) {
        throw new Error('No refresh token available');
      }
      const response = await axiosInstance.post(`${API_URL}/token/refresh/`, { refresh });
      if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
      }
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.error || 'Token refresh failed');
      }
      throw error;
    }
  },

  async logout(): Promise<void> {
    try {
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        await axiosInstance.post(`${API_URL}/logout/`, { refresh });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
};

export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export default authService; 