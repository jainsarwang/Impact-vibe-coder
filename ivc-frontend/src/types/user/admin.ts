
export interface User {
  id: string;
  username: string;
  password: string;
  email: string;
  isActive: boolean;
  tokensLeft: number;
  tokensUsed: number;
  totalTokens: number;
  lastLogin: string;
  projects: any[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  assignedUsers: string[];
  createdDate: string;
  status: 'active' | 'completed' | 'paused' | 'in-progress';
  category: string;
}

export interface Settings {
  organizationName: string;
  totalTokens: number;
  tokensRemaining: number;
  defaultTokenAllocation: number;
  autoTokenDistribution: boolean;
  notificationsEnabled: boolean;
  maintenanceMode: boolean;
}
