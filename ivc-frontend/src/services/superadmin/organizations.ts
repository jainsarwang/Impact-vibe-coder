import { baseURL, getAuthHeaders, handleApiError } from './base';
import { OrganizationsResponse, OrganizationResponse, AdminCreateRequest, AdminCreateResponse } from './types';

export const getAllOrganizations = async (): Promise<OrganizationsResponse> => {
  try {
    console.log('Fetching organizations from:', `${baseURL}/superadmin/organizations`);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    const response = await fetch(`${baseURL}/superadmin/organizations`, {
      method: 'GET',
      headers: getAuthHeaders(),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    console.log('Organizations response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch organizations');
    }

    const data = await response.json();
    console.log('Organizations data:', data);
    return data;
  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new Error('Request timeout - please check your connection');
    }
    return handleApiError(error);
  }
};

export const getOrganizationById = async (organizationId: string): Promise<OrganizationResponse> => {
  try {
    const allOrgs = await getAllOrganizations();
    const organization = allOrgs.organizations.find(org => org.organization_id === organizationId);
    
    if (!organization) {
      throw new Error('Organization not found');
    }

    return { organization };
  } catch (error: any) {
    return handleApiError(error);
  }
};

export const createAdminWithOrg = async (adminData: AdminCreateRequest): Promise<AdminCreateResponse> => {
  try {
    console.log('Creating admin with org - original data:', adminData);
    
    // Ensure the payload matches backend expectations
    const payload = {
      name: adminData.name.trim(),
      email: adminData.email.trim().toLowerCase(),
      organization_name: adminData.organization_name.trim(),
      total_tokens: Number(adminData.total_tokens) // Ensure it's a number, not string
    };
    
    console.log('Creating admin with org - formatted payload:', payload);
    
    // Validate payload before sending
    if (!payload.name || !payload.email || !payload.organization_name || !payload.total_tokens) {
      throw new Error('All fields are required');
    }
    
    if (payload.total_tokens <= 0) {
      throw new Error('Total tokens must be greater than 0');
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(payload.email)) {
      throw new Error('Invalid email format');
    }
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

    const response = await fetch(`${baseURL}/superadmin/create_admin_org`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    console.log('Create admin response status:', response.status);
    console.log('Create admin response headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (parseError) {
        console.error('Failed to parse error response:', parseError);
        throw new Error(`Request failed with status ${response.status}`);
      }
      
      console.error('Create admin error details:', errorData);
      
      // Handle specific validation errors
      if (response.status === 422) {
        const errorMessage = errorData.detail || 'Validation error - please check your input';
        if (typeof errorData.detail === 'object' && errorData.detail.length > 0) {
          // Handle array of validation errors
          const validationErrors = errorData.detail.map((err: any) => err.msg || err.message || err).join(', ');
          throw new Error(`Validation errors: ${validationErrors}`);
        }
        throw new Error(errorMessage);
      }
      
      throw new Error(errorData.detail || errorData.message || 'Failed to create admin with organization');
    }

    const responseData = await response.json();
    console.log('Create admin success response:', responseData);
    return responseData;
  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new Error('Request timeout - please try again');
    }
    console.error('Create admin error:', error);
    return handleApiError(error);
  }
};

export const updateOrganizationStatus = async (
  organizationName: string,
  isActive: boolean
): Promise<void> => {
  try {
    const status = isActive ? true : false;
    console.log('Updating organization status:', { organizationName, status, isActive });
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    const response = await fetch(
      `${baseURL}/organizations/status?organization_name=${encodeURIComponent(organizationName)}&status=${status}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
        signal: controller.signal,
      }
    );

    clearTimeout(timeoutId);
    console.log('Update status response:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Update status error:', errorData);
      throw new Error(errorData.detail || 'Failed to update organization status');
    }

    const result = await response.json();
    console.log('Status update result:', result);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout - please try again');
    }
    console.error('Status update error:', error);
    throw error;
  }
};

export const addTokensToOrganization = async (organizationName: string, tokens: number): Promise<void> => {
  try {
    console.log('Adding tokens to organization:', { organizationName, tokens });

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    const response = await fetch(
      `${baseURL}/superadmin/organizations/token_addition?organization_name=${encodeURIComponent(organizationName)}&tokens_to_be_added=${tokens}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
        signal: controller.signal,
      }
    );

    clearTimeout(timeoutId);
    console.log('Add tokens response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Add tokens error:', errorData);
      throw new Error(errorData.detail || 'Failed to add tokens to organization');
    }

    const result = await response.json();
    console.log('Token addition result:', result);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout - please try again');
    }
    console.error('Add tokens error:', error);
    throw error;
  }
};
