
import { AuthApiService } from './authApi';
import { UserApiService } from './userApi';
import { ProjectApiService } from './projectApi';
import { OrganizationApiService } from './organizationApi';

class ApiService {
  private authService: AuthApiService;
  private userService: UserApiService;
  private projectService: ProjectApiService;
  private organizationService: OrganizationApiService;

  constructor() {
    this.authService = new AuthApiService();
    this.userService = new UserApiService();
    this.projectService = new ProjectApiService();
    this.organizationService = new OrganizationApiService();
  }

  // Auth methods
  async login(username: string, password: string) {
    return this.authService.login(username, password);
  }

  async logout() {
    return this.authService.logout();
  }

  async getCurrentUser() {
    return this.authService.getCurrentUser();
  }

  async updateUserProfile(profileData: { username?: string; email?: string }) {
    return this.authService.updateUserProfile(profileData);
  }

  async verifyRole(role: string) {
    return this.authService.verifyRole(role);
  }

  // User management
  async getUsers() {
    return this.userService.getUsers();
  }

  async createUser(userData: { name: string; email: string; tokens: number }) {
    return this.userService.createUser(userData);
  }

  async updateUserTokens(userId: string, tokens: number) {
    return this.userService.updateUserTokens(userId, tokens);
  }

  async toggleUserStatus(userId: string) {
    return this.userService.toggleUserStatus(userId);
  }

  async deleteUser(userId: string) {
    return this.userService.deleteUser(userId);
  }

  async getUserTokens(userId?: string) {
    return this.userService.getUserTokens(userId);
  }

  async getUserDashboardData() {
    return this.userService.getUserDashboardData();
  }

  // Project management
  async getProjects() {
    return this.projectService.getProjects();
  }

  async getAllProjects() {
    return this.projectService.getAllProjects();
  }

  async createProject(projectData: { 
    name: string; 
    description: string; 
    assignedUser?: string;
    category: string;
    status?: string;
  }) {
    return this.projectService.createProject(projectData);
  }

  async updateProject(projectId: string, projectData: Partial<{ 
    name: string; 
    description: string; 
    status: string;
    category: string;
  }>) {
    return this.projectService.updateProject(projectId, projectData);
  }

  async updateProjectStatus(projectId: string, status: string) {
    return this.projectService.updateProjectStatus(projectId, status);
  }

  async deleteProject(projectId: string) {
    return this.projectService.deleteProject(projectId);
  }

  // Organization management
  async getOrganizationTokens(orgName: string) {
    return this.organizationService.getOrganizationTokens(orgName);
  }

  async getAllOrganizations() {
    return this.organizationService.getAllOrganizations();
  }

  async distributeTokensEqually(orgId: string) {
    return this.organizationService.distributeTokensEqually(orgId);
  }

  async addTokensToOrganization(orgName: string, tokens: number) {
    return this.organizationService.addTokensToOrganization(orgName, tokens);
  }

  async updateOrganizationStatus(orgName: string, status: string) {
    return this.organizationService.updateOrganizationStatus(orgName, status);
  }

  // Admin dashboard data
  async getAdminDashboardData() {
    try {
      const [users, projects, organizations] = await Promise.all([
        this.getUsers(),
        this.getAllProjects(),
        this.getAllOrganizations()
      ]);

      return {
        users: users || [],
        projects: projects || [],
        organizations: organizations || []
      };
    } catch (error) {
      console.error('Failed to fetch admin dashboard data:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();
