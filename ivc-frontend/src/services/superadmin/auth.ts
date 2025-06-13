
import { setCookie, deleteCookie } from 'cookies-next';
import { baseURL, getAuthHeaders, handleApiError } from './base';
import { User } from './types';

export const login = async (credentials: { username: string; password: string }): Promise<any> => {
  try {
    console.log('Attempting login to:', `${baseURL}/login`);
    
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${baseURL}/login`, {
      method: 'POST',
      body: formData,
    });

    console.log('Login response status:', response.status);
    const data = await response.json();
    console.log('Login response data:', data);

    if (!response.ok) {
      throw new Error(data.detail || 'Login failed');
    }

    setCookie('accessToken', data.access_token, { maxAge: 60 * 60 * 24 * 30, sameSite: 'lax' });
    return data;
  } catch (error: any) {
    return handleApiError(error);
  }
};

export const logout = async (): Promise<void> => {
  deleteCookie('accessToken');
};

export const verifySuperAdmin = async (): Promise<any> => {
  try {
    console.log('Verifying super admin with:', `${baseURL}/auth/superadmin`);
    const response = await fetch(`${baseURL}/auth/superadmin`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    
    console.log('Super admin verification response status:', response.status);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'SuperAdmin verification failed');
    }
    
    return response.json();
  } catch (error) {
    return handleApiError(error);
  }
};

export const verifyAdmin = async (): Promise<any> => {
  try {
    const response = await fetch(`${baseURL}/auth/admin`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Admin verification failed');
    }
    
    return response.json();
  } catch (error) {
    return handleApiError(error);
  }
};

export const verifyUser = async (): Promise<any> => {
  try {
    const response = await fetch(`${baseURL}/auth/user`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'User verification failed');
    }
    
    return response.json();
  } catch (error) {
    return handleApiError(error);
  }
};

export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await fetch(`${baseURL}/auth/me`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get current user');
    }

    return await response.json();
  } catch (error) {
    return handleApiError(error);
  }
};
