
import { BaseApiService } from './baseApi';

export class AdminApiService extends BaseApiService {
  async getAdminDashboardData() {
    try {
      // Get current user first
      const currentUser = await this.getCurrentUser();
      console.log('Current user:', currentUser);
      
      // Use organization/get_user endpoint instead of superadmin/organizations
      const response = await fetch(`${this.baseURL}/organization/get_users`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch organization data: ${response.status} - ${errorText}`);
      }

      const orgData = await response.json();
      console.log('Organization data:', orgData);
      
      // Transform users data from API response
      const users = (orgData.users || []).map((user: any) => ({
        id: user.user_id,
        username: user.username,
        email: user.email || '',
        isActive: user.is_active,
        tokensLeft: user.tokens || 0,
        tokensUsed: user.tokens_used || 0,
        totalTokens: (user.tokens || 0) + (user.tokens_used || 0),
        lastLogin: user.last_login || user.created_at || 'Never',
        projects: []
      }));

      // Get projects for users
      const projects = [];
      for (const user of (orgData.users || [])) {
        try {
          const userResponse = await fetch(`${this.baseURL}/users/${user.username}`, {
            method: 'GET',
            headers: this.getAuthHeaders(),
          });
          
          if (userResponse.ok) {
            const userInfo = await userResponse.json();
            if (userInfo.projects) {
              userInfo.projects.forEach((project: any) => {
                projects.push({
                  id: project.project_id,
                  name: project.project_name,
                  description: project.description || '',
                  assignedUsers: [user.username],
                  createdDate: project.created_at || new Date().toISOString(),
                  status: project.is_deployed ? 'completed' : 'in-progress',
                  category: 'Development'
                });
              });
            }
          }
        } catch (error) {
          console.warn(`Failed to fetch projects for user ${user.username}`);
        }
      }

      return {
        users,
        projects,
        settings: {
          organizationName: orgData.organization_name || 'Organization',
          totalTokens: orgData.total_tokens || 0,
          tokensRemaining: orgData.tokens_remaining || 0,
          defaultTokenAllocation: 1000,
          autoTokenDistribution: false,
          notificationsEnabled: true,
          maintenanceMode: false
        }
      };
    } catch (error) {
      console.error('Failed to fetch admin dashboard data:', error);
      throw error;
    }
  }

  async createUser(userData: { name: string; email: string; tokens: number }) {
    const response = await fetch(`${this.baseURL}/admin/create_user`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        name: userData.name,
        email: userData.email,
        tokens: userData.tokens || 0
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to create user: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async createProject(projectData: { 
    name: string; 
    description: string; 
    assignedUser?: string;
    category: string;
    status?: string;
  }) {
    console.warn('Create project endpoint not implemented in FastAPI backend');
    return { 
      success: true, 
      project_id: `proj_${Date.now()}`,
      project_name: projectData.name,
      description: projectData.description
    };
  }

  async distributeTokensEqually(orgId: string) {
    const response = await fetch(`${this.baseURL}/organizations/${orgId}/distribute_tokens`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to distribute tokens: ${response.status} - ${errorText}`);
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

  async updateUserTokens(userId: string, tokens: number) {
    const response = await fetch(`${this.baseURL}/admin/users/${userId}/update_tokens`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ tokens }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to update user tokens: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async updateUserProfile(profileData: { username?: string; email?: string }) {
    const response = await fetch(`${this.baseURL}/auth/update_profile`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to update user profile: ${response.status} - ${errorText}`);
    }

    return response.json();
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
