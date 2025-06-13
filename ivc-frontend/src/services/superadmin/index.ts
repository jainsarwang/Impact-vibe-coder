
import * as auth from './auth';
import * as organizations from './organizations';
import * as users from './users';
import * as base from './base';

export class AdminApiService {
  // Auth methods
  login = auth.login;
  logout = auth.logout;
  verifySuperAdmin = auth.verifySuperAdmin;
  verifyAdmin = auth.verifyAdmin;
  verifyUser = auth.verifyUser;
  getCurrentUser = auth.getCurrentUser;

  // Organization methods
  getAllOrganizations = organizations.getAllOrganizations;
  getOrganizationById = organizations.getOrganizationById;
  createAdminWithOrg = organizations.createAdminWithOrg;
  updateOrganizationStatus = organizations.updateOrganizationStatus;
  addTokensToOrganization = organizations.addTokensToOrganization;

  // User methods
  getUserByUsername = users.getUserByUsername;

  // Base methods
  healthCheck = base.healthCheck;
}

export const adminApiService = new AdminApiService();

// Export types
export * from './types';
