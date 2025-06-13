import React, { useState, useEffect } from 'react';
import { useToast } from '@/hooks/superadmin/use-toast';
import { adminApiService, type Organization } from '@/services/superadmin/adminApi';
import OrganizationHeader from './organization/OrganizationHeader';
import OrganizationStatsCards from './organization/OrganizationStatsCards';
import PrimaryAdminSection from './organization/PrimaryAdminSection';
import AddTokensDialog from './organization/AddTokensDialog';

interface OrganizationDetailsProps {
  orgId: string;
  onBack: () => void;
  onViewAdmin: (adminId: string) => void;
  onTokensUpdated?: () => void;
}

const OrganizationDetails = ({ orgId, onBack, onViewAdmin, onTokensUpdated }: OrganizationDetailsProps) => {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddTokenDialog, setShowAddTokenDialog] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadOrganizationDetails();
  }, [orgId]);

  const loadOrganizationDetails = async () => {
    try {
      setIsLoading(true);
      const response = await adminApiService.getAllOrganizations();
      const foundOrg = response.organizations.find(org => org.organization_id === orgId);
      
      if (foundOrg) {
        setOrganization(foundOrg);
      } else {
        toast({
          title: "Error",
          description: "Organization not found",
          variant: "destructive"
        });
        onBack();
      }
    } catch (error) {
      console.error('Error loading organization details:', error);
      toast({
        title: "Error",
        description: "Failed to load organization details",
        variant: "destructive"
      });
      onBack();
    } finally {
      setIsLoading(false);
    }
  };

  const handleTokensAdded = () => {
    // Reload local details
    loadOrganizationDetails();
    // Notify parent to update dashboard
    if (onTokensUpdated) {
      onTokensUpdated();
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-blue-600"></div>
          <p className="mt-3 text-gray-600 text-sm">Loading organization details...</p>
        </div>
      </div>
    );
  }

  if (!organization) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Organization not found</p>
          <button onClick={onBack} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded">Go Back</button>
        </div>
      </div>
    );
  }

  const primaryAdmin = organization.users?.find(user => user.is_primary_admin);
  const isOrganizationActive = organization.is_active !== undefined ? organization.is_active : true;

  return (
    <div className="min-h-screen bg-gray-50">
      <OrganizationHeader organization={organization} onBack={onBack} />

      <div className="max-w-6xl mx-auto px-4 py-6">
        <OrganizationStatsCards organization={organization} />

        {primaryAdmin && (
          <PrimaryAdminSection 
            primaryAdmin={primaryAdmin}
            organizationActive={isOrganizationActive}
            onAddTokens={() => setShowAddTokenDialog(true)}
          />
        )}
      </div>

      <AddTokensDialog
        isOpen={showAddTokenDialog}
        onClose={() => setShowAddTokenDialog(false)}
        organization={organization}
        onTokensAdded={handleTokensAdded}
      />
    </div>
  );
};

export default OrganizationDetails;
