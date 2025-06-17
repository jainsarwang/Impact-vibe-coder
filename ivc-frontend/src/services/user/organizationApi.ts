
import { BaseApiService } from './baseApi';

export class OrganizationApiService extends BaseApiService {
  async getOrganizationTokens(orgName: string) {
    const response = await fetch(`${this.baseURL}/organizations/${encodeURIComponent(orgName)}/tokens`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get organization tokens: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async getAllOrganizations() {
    try {
      const response = await fetch(`${this.baseURL}/superadmin/organizations`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        if (response.status === 403) {
          // User doesn't have superadmin access, return empty organizations
          console.log('User does not have superadmin access to view all organizations');
          return { organizations: [] };
        }
        const errorText = await response.text();
        throw new Error(`Failed to get all organizations: ${response.status} - ${errorText}`);
      }

      return response.json();
    } catch (error) {
      console.warn('Failed to fetch organizations:', error);
      return { organizations: [] };
    }
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

  async addTokensToOrganization(orgName: string, tokens: number) {
    const response = await fetch(`${this.baseURL}/superadmin/organizations/token_addition?organization_name=${encodeURIComponent(orgName)}&tokens_to_be_added=${tokens}`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to add tokens to organization: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async updateOrganizationStatus(orgName: string, status: string) {
    const response = await fetch(`${this.baseURL}/organizations/status?organization_name=${encodeURIComponent(orgName)}&status=${status}`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to update organization status: ${response.status} - ${errorText}`);
    }

    return response.json();
  }
}
