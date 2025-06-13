
import { BaseApiService } from './baseApi';

export class AuthApiService extends BaseApiService {
  async login(username: string, password: string) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Authentication failed: ${errorText}`);
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async logout() {
    this.clearToken();
  }

  async getCurrentUser() {
    const response = await fetch(`${this.baseURL}/auth/me`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get current user: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async updateUserProfile(profileData: { username?: string; email?: string }) {
    // This endpoint doesn't exist in your FastAPI backend, but we need it for the API service
    console.warn('Update user profile endpoint not implemented in FastAPI backend');
    return { success: true, message: 'Profile update not implemented' };
  }

  async verifyRole(role: string) {
    const response = await fetch(`${this.baseURL}/auth/${role}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to verify role: ${response.status} - ${errorText}`);
    }

    return response.json();
  }
}
