
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, Building2 } from 'lucide-react';
import { useOrganizationCreation } from '@/hooks/superadmin/useOrganizationCreation';

interface Credentials {
  username: string;
  password: string;
  organizationName: string;
}

interface CreateOrganizationDialogProps {
  onOrganizationCreated: (credentials?: Credentials) => void;
  existingOrganizations?: any[];
}

const CreateOrganizationDialog = ({ onOrganizationCreated, existingOrganizations }: CreateOrganizationDialogProps) => {
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const {
    formData,
    setFormData,
    isCreating,
    createOrganization,
  } = useOrganizationCreation(existingOrganizations);

  const handleCreateOrganization = async () => {
    console.log('Creating organization...');
    const newCredentials = await createOrganization();
    
    if (newCredentials) {
      console.log('Organization created successfully, closing create dialog and passing credentials');
      setShowCreateDialog(false);
      // Pass credentials to parent
      onOrganizationCreated(newCredentials);
    } else {
      console.log('Failed to create organization');
    }
  };

  const handleCreateDialogClose = (open: boolean) => {
    setShowCreateDialog(open);
  };

  return (
    <Dialog open={showCreateDialog} onOpenChange={handleCreateDialogClose}>
      <DialogTrigger asChild>
        <Button className="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white text-xs h-7 px-2">
          <Plus className="w-3 h-3 mr-1" />
          Create Organization
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center text-base">
            <Building2 className="w-4 h-4 mr-2" />
            Create New Organization
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <Label htmlFor="adminName" className="text-xs">Admin Name</Label>
            <Input
              id="adminName"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="Enter admin full name"
              className="text-xs h-7"
            />
          </div>
          <div>
            <Label htmlFor="adminEmail" className="text-xs">Admin Email</Label>
            <Input
              id="adminEmail"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="Enter admin email"
              className="text-xs h-7"
            />
          </div>
          <div>
            <Label htmlFor="orgName" className="text-xs">Organization Name</Label>
            <Input
              id="orgName"
              value={formData.organization_name}
              onChange={(e) => setFormData({...formData, organization_name: e.target.value})}
              placeholder="Enter organization name"
              className="text-xs h-7"
            />
          </div>
          <div>
            <Label htmlFor="tokens" className="text-xs">Initial Tokens</Label>
            <Input
              id="tokens"
              type="number"
              value={formData.total_tokens}
              onChange={(e) => setFormData({...formData, total_tokens: e.target.value})}
              placeholder="Enter number of tokens"
              min="1"
              className="text-xs h-7"
            />
          </div>
          <div className="flex space-x-2 pt-2">
            <Button 
              onClick={handleCreateOrganization} 
              className="flex-1 text-xs h-7"
              disabled={isCreating}
            >
              {isCreating ? "Creating..." : "Create Organization"}
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setShowCreateDialog(false)}
              className="flex-1 text-xs h-7"
            >
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateOrganizationDialog;
