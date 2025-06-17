
import React, { useState, useEffect } from 'react';
import { useToast } from '@/hooks/superadmin/use-toast';
import { adminApiService, type Organization } from '@/services/superadmin/adminApi';
import { ThemeProvider } from '@/hooks/superadmin/useTheme';
import OrganizationDetails from './OrganizationDetails';
import AdminDetails from './AdminDetails';
import DashboardHeader from './dashboard/DashboardHeader';
import StatsOverview from './dashboard/StatsOverview';
import ActionsBar from './dashboard/ActionsBar';
import OrganizationCard from './dashboard/OrganizationCard';
import OrganizationSearch from './dashboard/OrganizationSearch';
import CredentialsDialog from './dashboard/CredentialsDialog';

interface SuperAdminDashboardProps {
  onLogout: () => void;
}

interface Credentials {
  username: string;
  password: string;
  organizationName: string;
}

const SuperAdminDashboard = ({ onLogout }: SuperAdminDashboardProps) => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [filteredOrganizations, setFilteredOrganizations] = useState<Organization[]>([]);
  const [selectedView, setSelectedView] = useState<'overview' | 'organization' | 'admin'>('overview');
  const [selectedId, setSelectedId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  
  // Move credentials state to parent to prevent loss on re-renders
  const [credentials, setCredentials] = useState<Credentials>({ 
    username: '', 
    password: '', 
    organizationName: '' 
  });
  const [showCredentialsDialog, setShowCredentialsDialog] = useState(false);
  
  const { toast } = useToast();

  useEffect(() => {
    loadOrganizations();
  }, []);

  useEffect(() => {
    setFilteredOrganizations(organizations);
  }, [organizations]);

  // Watch for credentials to show dialog
  useEffect(() => {
    console.log('Dashboard credentials changed:', credentials);
    if (credentials.username && credentials.password && credentials.organizationName) {
      console.log('Valid credentials received in dashboard, showing dialog');
      setShowCredentialsDialog(true);
    }
  }, [credentials]);

  const loadOrganizations = async () => {
    try {
      setIsLoading(true);
      console.log('Loading organizations...');
      const response = await adminApiService.getAllOrganizations();
      console.log('Organizations loaded:', response.organizations);
      setOrganizations(response.organizations);
      setFilteredOrganizations(response.organizations);
    } catch (error) {
      console.error('Error loading organizations:', error);
      toast({
        title: "Error",
        description: "Failed to load organizations",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Real-time update function that preserves search filter
  const updateOrganizationsRealTime = async () => {
    try {
      console.log('Updating organizations in real-time...');
      const response = await adminApiService.getAllOrganizations();
      console.log('Real-time update:', response.organizations);
      
      setOrganizations(response.organizations);
      
      // Preserve current search filter
      const currentSearchTerm = getCurrentSearchTerm();
      if (currentSearchTerm) {
        const filtered = response.organizations.filter(org => 
          org.organization_name.toLowerCase().includes(currentSearchTerm.toLowerCase()) ||
          org.organization_id.toLowerCase().includes(currentSearchTerm.toLowerCase())
        );
        setFilteredOrganizations(filtered);
      } else {
        setFilteredOrganizations(response.organizations);
      }
    } catch (error) {
      console.error('Error updating organizations:', error);
    }
  };

  const getCurrentSearchTerm = () => {
    // Simple way to detect if we're in a filtered state
    return organizations.length > filteredOrganizations.length ? 'filtered' : '';
  };

  const totalStats = {
    organizations: organizations.length,
    admins: organizations.reduce((sum, org) => sum + (org.users?.filter(user => user.role_id && !user.role_id.includes('user')).length || 0), 0),
    users: organizations.reduce((sum, org) => sum + (org.user_count || 0), 0),
    activeOrgs: organizations.filter(org => org.is_active !== false).length
  };

  const handleLogout = () => {
    adminApiService.logout();
    onLogout();
  };

  const handleOrganizationCreated = (newCredentials?: Credentials) => {
    console.log('Organization created, updating dashboard and setting credentials...', newCredentials);
    
    // Set credentials if provided
    if (newCredentials) {
      console.log('Setting credentials in dashboard:', newCredentials);
      setCredentials(newCredentials);
    }
    
    // Update organizations list
    updateOrganizationsRealTime();
  };

  const handleOrganizationStatusUpdated = () => {
    console.log('Organization status updated, refreshing dashboard...');
    updateOrganizationsRealTime();
  };

  const handleTokensUpdated = () => {
    console.log('Tokens updated, refreshing dashboard...');
    updateOrganizationsRealTime();
  };

  const handleViewOrganization = (orgId: string) => {
    setSelectedId(orgId);
    setSelectedView('organization');
  };

  const handleViewAdmin = (adminId: string) => {
    setSelectedId(adminId);
    setSelectedView('admin');
  };

  const handleSearch = (searchTerm: string) => {
    if (!searchTerm.trim()) {
      setFilteredOrganizations(organizations);
      return;
    }

    const filtered = organizations.filter(org => 
      org.organization_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      org.organization_id.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredOrganizations(filtered);
  };

  const handleCredentialsClose = () => {
    console.log('Closing credentials dialog from dashboard');
    setShowCredentialsDialog(false);
    setCredentials({ username: '', password: '', organizationName: '' });
  };

  if (selectedView === 'organization') {
    return (
      <ThemeProvider>
        <OrganizationDetails 
          orgId={selectedId} 
          onBack={() => setSelectedView('overview')} 
          onViewAdmin={handleViewAdmin}
          onTokensUpdated={handleTokensUpdated}
        />
      </ThemeProvider>
    );
  }

  if (selectedView === 'admin') {
    return (
      <ThemeProvider>
        <AdminDetails adminId={selectedId} onBack={() => setSelectedView('organization')} onViewUser={() => {}} />
      </ThemeProvider>
    );
  }

  if (isLoading) {
    return (
      <ThemeProvider>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-blue-600"></div>
            <p className="mt-3 text-gray-600 dark:text-gray-300 text-sm">Loading dashboard...</p>
          </div>
        </div>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <DashboardHeader onLogout={handleLogout} />

        <div className="max-w-7xl mx-auto px-4 py-6">
          <StatsOverview totalStats={totalStats} />

          <ActionsBar 
            organizations={organizations} 
            onOrganizationCreated={handleOrganizationCreated}
          />

          <OrganizationSearch onSearch={handleSearch} />

          {/* Organizations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredOrganizations.map((org) => (
              <OrganizationCard 
                key={org.organization_id} 
                org={org} 
                onViewOrganization={handleViewOrganization}
                onStatusUpdated={handleOrganizationStatusUpdated}
              />
            ))}
          </div>

          {filteredOrganizations.length === 0 && organizations.length > 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">No organizations found matching your search.</p>
            </div>
          )}
        </div>

        {/* Credentials Dialog */}
        <CredentialsDialog
          isOpen={showCredentialsDialog}
          onClose={handleCredentialsClose}
          username={credentials.username}
          password={credentials.password}
          organizationName={credentials.organizationName}
        />
      </div>
    </ThemeProvider>
  );
};

export default SuperAdminDashboard;
