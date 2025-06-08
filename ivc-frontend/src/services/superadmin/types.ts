
export interface User {
  user_id: string;
  email: string;
  name: string;
  username?: string;
  role_id: string;
  organization_id: string;
  is_active: boolean;
  is_primary_admin: boolean;
  tokens?: number;
  tokens_allowed?: number;
  created_at: string;
  updated_at: string;
}

export interface Organization {
  organization_id: string;
  organization_name: string;
  total_tokens: number;
  tokens_remaining: number;
  user_count: number;
  is_active?: boolean;
  created_at: string;
  updated_at: string;
  users?: User[];
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface OrganizationsResponse {
  organizations: Organization[];
}

export interface OrganizationResponse {
  organization: Organization;
}

export interface UsersResponse {
  users: User[];
}

export interface UserResponse {
  user: User;
}

export interface AdminCreateRequest {
  name: string;
  email: string;
  organization_name: string;
  total_tokens: number;
}

export interface AdminCreateResponse {
  username: string;
  password: string;
  organization_id: string;
  user_id: string;
}
