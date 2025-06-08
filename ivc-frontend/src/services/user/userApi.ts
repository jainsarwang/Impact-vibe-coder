
import { BaseApiService } from './baseApi';

export class UserApiService extends BaseApiService {
  async getUsers() {
    try {
      // Get current user first to determine their organization
      const currentUser = await this.getCurrentUser();
      console.log('Current user:', currentUser);
      
      // Get organization data which includes users
      const response = await fetch(`${this.baseURL}/organizations/get_users`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to get organizations: ${response.status} - ${errorText}`);
      }

      const orgData = await response.json();
      
      // Find the organization that contains the current user
      const userOrg = orgData.organizations?.find((org: any) => 
        org.users.some((user: any) => user.user_id === currentUser.user_id)
      );
      
      return userOrg?.users || [];
    } catch (error) {
      console.error('Failed to fetch users:', error);
      return [];
    }
  }

  async createUser(userData: { name: string; email: string; tokens: number }) {
    const response = await fetch(`${this.baseURL}/admin/create_user`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        name: userData.name,
        email: userData.email
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to create user: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async updateUserTokens(userId: string, tokens: number) {
    const response = await fetch(`${this.baseURL}/admin/users/${userId}/update_tokens?tokens=${tokens}`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to update user tokens: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async toggleUserStatus(userId: string) {
    const response = await fetch(`${this.baseURL}/admin/users/${userId}/toggle_status`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to toggle user status: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async deleteUser(userId: string) {
    // This endpoint doesn't exist in your FastAPI backend
    console.warn('Delete user endpoint not implemented in FastAPI');
    return { success: true };
  }

  async getUserTokens(username?: string) {
    if (username) {
      // Get specific user info by username
      const response = await fetch(`${this.baseURL}/users/${username}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to get user tokens: ${response.status} - ${errorText}`);
      }

      const user = await response.json();
      return {
        available: user.tokens_allowed || 0,
        used: user.tokens_consumed || 0,
        total: user.tokens_allowed || 0
      };
    } else {
      // Get current user tokens
      const user = await this.getCurrentUser();
      return {
        available: user.tokens || 0,
        used: 0,
        total: user.tokens || 0
      };
    }
  }

  async getUserDashboardData() {
    try {
      const user = await this.getCurrentUser();
      console.log('Current user data:', user);
      
      const response = await fetch(`${this.baseURL}/users/${user.username}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to get user info: ${response.status} - ${errorText}`);
      }

      const userInfo = await response.json();
      console.log('User info with projects:', userInfo);
      
      return {
        user: {
          username: user.username,
          email: user.email || '',
          tokensLeft: user.tokens || 0,
          tokensUsed: 0,
          totalTokens: user.tokens || 0,
        },
        projects: userInfo.projects || []
      };
    } catch (error) {
      console.error('Failed to fetch user dashboard data:', error);
      throw error;
    }
  }

  private async getCurrentUser() {
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
}
