
import { BaseApiService } from './baseApi';

export class ProjectApiService extends BaseApiService {
  async getProjects() {
    try {
      const user = await this.getCurrentUser();
      const userInfo = await this.request<any>(`/users/${user.username}`);
      return userInfo.projects || [];
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      return [];  
    }
  }

  async getAllProjects() {
    try {
      // For admin users, get all projects in their organization
      const currentUser = await this.getCurrentUser();
      const orgData = await this.request<any>('/organization/get_users');
      
      const userOrg = orgData.organizations?.find((org: any) => 
        org.users.some((user: any) => user.user_id === currentUser.user_id)
      );
      
      if (!userOrg) return [];
      
      // Get all projects for users in this organization
      const allProjects = [];
      for (const user of userOrg.users) {
        try {
          const userInfo = await this.request<any>(`/users/${user.username}`);
          if (userInfo.projects) {
            allProjects.push(...userInfo.projects.map((p: any) => ({
              ...p,
              assigned_users: [user.username]
            })));
          }
        } catch (error) {
          console.warn(`Failed to fetch projects for user ${user.username}`);
        }
      }
      
      return allProjects;
    } catch (error) {
      console.error('Failed to fetch all projects:', error);
      return [];
    }
  }

  async createProject(projectData: { 
    name: string; 
    description: string; 
    assignedUser?: string;
    category: string;
    status?: string;
  }) {
    // This endpoint doesn't exist in the FastAPI you provided
    console.warn('Create project endpoint not implemented in FastAPI');
    return { 
      success: true, 
      project_id: `proj_${Date.now()}`,
      project_name: projectData.name,
      description: projectData.description
    };
  }

  async updateProject(projectId: string, projectData: Partial<{ 
    name: string; 
    description: string; 
    status: string;
    category: string;
  }>) {
    // This endpoint doesn't exist in your FastAPI
    console.warn('Update project endpoint not implemented in FastAPI');
    return { success: true };
  }

  async updateProjectStatus(projectId: string, status: string) {
    // This endpoint doesn't exist in your FastAPI
    console.warn('Update project status endpoint not implemented in FastAPI');
    return { success: true };
  }

  async deleteProject(projectId: string) {
    // This endpoint doesn't exist in your FastAPI
    console.warn('Delete project endpoint not implemented in FastAPI');
    return { success: true };
  }

  private async getCurrentUser() {
    return this.request<any>('/auth/me');
  }
}
